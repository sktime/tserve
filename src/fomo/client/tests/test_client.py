from unittest.mock import MagicMock

import pytest

from fomo.client.client import Client
from fomo.types.converters import coerce_request, coerce_response, encode_request, encode_response
from fomo.types.models import ForecastRequest, ForecastResponse, HealthResult, ModelsResult, StatsResult


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


client = Client("http://example", transport=MagicMock())


@pytest.mark.parametrize(
    "history",
    [
        pytest.param(
            {
                "timestamp": ["2024-01-01"],
                "sales": [120],
            },
            id="column_dict",
        ),
        pytest.param(
            {
                "columns": ["timestamp", "sales"],
                "data": [
                    ["2024-01-01", 120],
                ],
            },
            id="columns_data",
        ),
    ],
)
def test_forecast(history):
    client._transport.reset_mock()
    payload = _request(history=history)
    encoded = encode_request(coerce_request(ForecastRequest.model_validate(payload)))
    client._transport.forecast.return_value = encode_response(
        coerce_response(_response())
    )

    result = client.forecast(**payload)

    assert isinstance(result, ForecastResponse)
    assert isinstance(result.predictions, dict)
    if set(history) == {"columns", "data"}:
        assert set(result.predictions) == {"columns", "data"}
    else:
        assert "timestamp" in result.predictions
        assert "sales" in result.predictions
        assert "columns" not in result.predictions
    assert result.model == "naive"
    assert result.request_id == "req-1"
    client._transport.forecast.assert_called_once_with(*encoded)


def test_health():
    client._transport.reset_mock()
    client._transport.health.return_value = HealthResult(status="ok")

    assert client.health() == HealthResult(status="ok")
    client._transport.health.assert_called_once_with()


def test_models():
    client._transport.reset_mock()
    client._transport.models.return_value = ModelsResult(models=[])

    assert client.models() == ModelsResult(models=[])
    client._transport.models.assert_called_once_with()


def test_stats():
    client._transport.reset_mock()
    expected = StatsResult.model_validate(
        {"uptime_s": 1.0, "memory": {}, "models": {}}
    )
    client._transport.stats.return_value = expected

    assert client.stats() is expected
    client._transport.stats.assert_called_once_with()


def test_close():
    client._transport.reset_mock()
    client.close()
    client._transport.close.assert_called_once_with()


def test_context_manager():
    client._transport.reset_mock()
    with client as _:
        pass

    client._transport.close.assert_called_once_with()
