import json
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tserve.logging.stats import Stats
from tserve.server.routes import router
from tserve.types.converters import (
    coerce_request,
    coerce_response,
    decode_response,
    encode_request,
    unpack_envelope,
)
from tserve.types.models import ModelInfo, ModelsResult, PredictRequest, PredictResponse


def _request(**kwargs):
    payload = {
        "past": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return PredictRequest.model_validate(payload)


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return PredictResponse.model_validate(payload)


def _payload(**kwargs):
    payload = {
        "past": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return payload


def _runtime():
    runtime = MagicMock()
    runtime.loaded_models.return_value = ModelsResult(
        models=[ModelInfo(id="naive", executor="sktime", source="registry")]
    )
    runtime.stats = Stats()
    runtime.stats.register("naive", "sktime", 1.0, 0.5)
    runtime.scheduler.run.return_value = coerce_response(_response())
    return runtime


def _client(runtime):
    app = FastAPI()
    app.state.runtime = runtime
    app.include_router(router)
    return TestClient(app)


def test_dashboard():
    result = _client(_runtime()).get("/")

    assert result.status_code == 200
    assert result.headers["content-type"].startswith("text/html")
    assert "<title>TServe" in result.text
    assert 'id="quantiles-toggle"' in result.text
    assert 'id="quantiles-toggle" checked' not in result.text


def test_static_assets():
    client = _client(_runtime())

    for path, content_type in [
        ("/static/index.html", "text/html"),
        ("/favicon.ico", "image/svg+xml"),
    ]:
        result = client.get(path)
        assert result.status_code == 200, path
        assert result.headers["content-type"].startswith(content_type), path


def test_health():
    result = _client(_runtime()).get("/health")

    assert result.status_code == 200
    assert result.json() == {"status": "ok"}


def test_models():
    result = _client(_runtime()).get("/models")

    assert result.status_code == 200
    assert result.json() == {
        "models": [{"id": "naive", "executor": "sktime", "source": "registry"}]
    }


def test_stats():
    result = _client(_runtime()).get("/stats")

    assert result.status_code == 200
    body = result.json()
    assert body["uptime_s"] >= 0
    assert "naive" in body["models"]
    assert body["models"]["naive"]["executor"] == "sktime"


def test_predict():
    runtime = _runtime()
    result = _client(runtime).post("/predict", json=_payload())

    assert result.status_code == 200
    body = result.json()
    assert body["model"] == "naive"
    assert isinstance(body["predictions"], dict)
    assert body["request_id"]
    runtime.scheduler.run.assert_called_once()


def test_predict_bytes():
    runtime = _runtime()
    metadata, files = encode_request(coerce_request(_request()))

    result = _client(runtime).post(
        "/predict/bytes",
        data={"metadata": json.dumps(metadata)},
        files={
            "past": (
                "past",
                files["past"],
                "application/vnd.apache.arrow.stream",
            )
        },
    )

    assert result.status_code == 200
    assert result.headers["content-type"].startswith(
        "application/vnd.tserve.predict+arrow"
    )
    decoded = decode_response(*unpack_envelope(result.content))
    assert decoded.model == "naive"
    runtime.scheduler.run.assert_called_once()


@pytest.mark.parametrize(
    "exc",
    [
        pytest.param(ValueError("past is missing columns: ['date']"), id="value_error"),
        pytest.param(
            RuntimeError("model 'chronos_2' is not loaded on this server"),
            id="runtime_error",
        ),
        pytest.param(TypeError("boom"), id="type_error"),
    ],
)
def test_predict_errors_use_generic_http_exception(exc):
    runtime = _runtime()
    runtime.scheduler.run.side_effect = exc

    result = _client(runtime).post("/predict", json=_payload())

    assert result.status_code == 400
    detail = result.json()["detail"]
    assert detail["code"] == "request_failed"
    assert detail["error"] == str(exc)
    assert detail["request_id"]


def test_predict_get():
    result = _client(_runtime()).get("/predict")

    assert result.status_code == 405
    assert "POST /predict" in result.json()["detail"]
