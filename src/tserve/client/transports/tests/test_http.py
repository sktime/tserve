import json
from unittest.mock import MagicMock, patch

import pytest

from tserve.client.transports.http import HttpTransport
from tserve.types.converters import coerce_response, encode_response, pack_envelope
from tserve.types.models import HealthResult, ModelsResult, PredictResponse, StatsResult


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return PredictResponse.model_validate(payload)


def _http(ok):
    http = MagicMock()
    http.request.return_value = ok
    with patch("tserve.client.transports.http.httpx.Client", return_value=http):
        transport = HttpTransport("http://example")
    return transport, http


def _ok(**kwargs):
    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.content = b""
    response.json.return_value = {}
    for key, value in kwargs.items():
        setattr(response, key, value)
    return response


def test_uses_injected_client():
    http = MagicMock()
    http.request.return_value = _ok()
    http.request.return_value.json.return_value = {"status": "ok"}

    transport = HttpTransport("http://example", httpx_client=http)

    result = transport.health()

    http.request.assert_called_once_with("GET", "/health")
    assert result == HealthResult(status="ok")


def test_predict():
    metadata, files = encode_response(coerce_response(_response()))
    transport, http = _http(_ok(content=pack_envelope(metadata, files)))

    got_metadata, got_files = transport.predict(
        {"time": "timestamp", "model": "naive"},
        {"past": b"arrow"},
    )

    http.request.assert_called_once()
    method, path = http.request.call_args.args
    assert method == "POST"
    assert path == "/predict/bytes"
    assert (
        json.loads(http.request.call_args.kwargs["data"]["metadata"])["model"]
        == "naive"
    )
    assert "past" in http.request.call_args.kwargs["files"]
    assert got_metadata["model"] == "naive"
    assert "predictions" in got_files


def test_health():
    transport, http = _http(_ok())
    http.request.return_value.json.return_value = {"status": "ok"}

    result = transport.health()

    http.request.assert_called_once_with("GET", "/health")
    assert result == HealthResult(status="ok")


def test_models():
    payload = {"models": [{"id": "naive", "executor": "sktime", "source": "registry"}]}
    transport, http = _http(_ok())
    http.request.return_value.json.return_value = payload

    result = transport.models()

    http.request.assert_called_once_with("GET", "/models")
    assert result == ModelsResult.model_validate(payload)


def test_stats():
    payload = {"uptime_s": 1.0, "memory": {}, "models": {}}
    transport, http = _http(_ok())
    http.request.return_value.json.return_value = payload

    result = transport.stats()

    http.request.assert_called_once_with("GET", "/stats")
    assert result == StatsResult.model_validate(payload)


def test_close():
    transport, http = _http(_ok())

    transport.close()

    http.close.assert_called_once()


def test_json_error_raises_runtime_error():
    response = _ok()
    response.status_code = 400
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {
        "detail": {
            "error": "nope",
            "code": "request_failed",
            "request_id": "req-1",
        }
    }
    transport, _ = _http(response)

    with pytest.raises(RuntimeError, match=r"^nope$"):
        transport.health()


def test_non_json_error_raises_runtime_error():
    response = _ok()
    response.status_code = 404
    response.headers = {"content-type": "text/plain"}
    response.text = "Not Found"
    transport, _ = _http(response)

    with pytest.raises(RuntimeError, match="Not Found"):
        transport.health()
