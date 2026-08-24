from unittest.mock import MagicMock, patch

from fomo.client.client import Client
from fomo.types.converters import coerce_response, encode_response
from fomo.types.models import ForecastResponse, HealthResult, ModelsResult, StatsResult


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
    return payload


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return ForecastResponse.model_validate(payload)


def _client():
    transport = MagicMock()
    with patch("fomo.client.client.HttpTransport", return_value=transport):
        client = Client("http://example")
    return client, transport


def test_forecast():
    client, transport = _client()
    transport.forecast.return_value = encode_response(coerce_response(_response()))

    result = client.forecast(**_request())

    assert type(result) is ForecastResponse
    assert type(result.predictions) is dict
    assert result.model == "naive"
    assert result.request_id == "req-1"
    transport.forecast.assert_called_once()


def test_health():
    client, transport = _client()
    transport.health.return_value = HealthResult(status="ok")

    assert client.health() == HealthResult(status="ok")
    transport.health.assert_called_once()


def test_models():
    client, transport = _client()
    transport.models.return_value = ModelsResult(models=[])

    assert client.models() == ModelsResult(models=[])
    transport.models.assert_called_once()


def test_stats():
    client, transport = _client()
    expected = StatsResult.model_validate(
        {"uptime_s": 1.0, "memory": {}, "models": {}}
    )
    transport.stats.return_value = expected

    assert client.stats() is expected
    transport.stats.assert_called_once()


def test_close():
    client, transport = _client()

    client.close()

    transport.close.assert_called_once()


def test_context_manager():
    client, transport = _client()

    with client as entered:
        assert entered is client

    transport.close.assert_called_once()
