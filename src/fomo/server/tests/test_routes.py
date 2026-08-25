import json
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fomo.logging.stats import Stats
from fomo.server.routes import router
from fomo.types.converters import (
    coerce_request,
    coerce_response,
    decode_response,
    encode_request,
    unpack_envelope,
)
from fomo.types.models import ForecastRequest, ForecastResponse, ModelInfo, ModelsResult


def _request(**kwargs):
    payload = {
        "history": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "horizon": 1,
        "context": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return ForecastRequest.model_validate(payload)


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return ForecastResponse.model_validate(payload)


def _payload(**kwargs):
    payload = {
        "history": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "horizon": 1,
        "context": 1,
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


def test_forecast():
    runtime = _runtime()
    result = _client(runtime).post("/forecast", json=_payload())

    assert result.status_code == 200
    body = result.json()
    assert body["model"] == "naive"
    assert isinstance(body["predictions"], dict)
    assert body["request_id"]
    runtime.scheduler.run.assert_called_once()


def test_forecast_bytes():
    runtime = _runtime()
    metadata, files = encode_request(coerce_request(_request()))

    result = _client(runtime).post(
        "/forecast/bytes",
        data={"metadata": json.dumps(metadata)},
        files={"history": ("history", files["history"], "application/vnd.apache.arrow.stream")},
    )

    assert result.status_code == 200
    assert result.headers["content-type"].startswith("application/vnd.fomo.forecast+arrow")
    decoded = decode_response(*unpack_envelope(result.content))
    assert decoded.model == "naive"
    runtime.scheduler.run.assert_called_once()


@pytest.mark.parametrize(
    ("exc", "status_code", "code"),
    [
        pytest.param(ValueError("bad input"), 400, "bad_request", id="bad_request"),
        pytest.param(RuntimeError("not loaded"), 503, "model_unavailable", id="model_unavailable"),
        pytest.param(TypeError("boom"), 500, "internal_error", id="internal_error"),
    ],
)
def test_forecast_errors(exc, status_code, code):
    runtime = _runtime()
    runtime.scheduler.run.side_effect = exc

    result = _client(runtime).post("/forecast", json=_payload())

    assert result.status_code == status_code
    detail = result.json()["detail"]
    assert detail["code"] == code
    assert detail["error"] == str(exc)
    assert detail["request_id"]
