from typing import cast
from unittest.mock import MagicMock

import pytest

from fomo.client.client import Client
from fomo.client.transports.base import BaseTransport
from fomo.types.converters import (
    coerce_request,
    coerce_response,
    encode_request,
    encode_response,
)
from fomo.types.models import (
    HealthResult,
    ModelsResult,
    PredictRequest,
    PredictResponse,
    StatsResult,
)


def _request(**kwargs):
    payload = {
        "past": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
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
    return PredictResponse.model_validate(payload)


_transport = MagicMock()
client = Client("http://example", transport=cast(BaseTransport, _transport))


@pytest.mark.parametrize(
    "past",
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
def test_predict(past):
    _transport.reset_mock()
    payload = _request(past=past)
    encoded = encode_request(coerce_request(PredictRequest.model_validate(payload)))
    _transport.predict.return_value = encode_response(coerce_response(_response()))

    result = client.predict(**payload)

    assert isinstance(result, PredictResponse)
    assert isinstance(result.predictions, dict)
    if set(past) == {"columns", "data"}:
        assert set(result.predictions) == {"columns", "data"}
    else:
        assert "timestamp" in result.predictions
        assert "sales" in result.predictions
        assert "columns" not in result.predictions
    assert result.model == "naive"
    assert result.request_id == "req-1"
    _transport.predict.assert_called_once_with(*encoded)


def test_health():
    _transport.reset_mock()
    _transport.health.return_value = HealthResult(status="ok")

    assert client.health() == HealthResult(status="ok")
    _transport.health.assert_called_once_with()


def test_models():
    _transport.reset_mock()
    _transport.models.return_value = ModelsResult(models=[])

    assert client.models() == ModelsResult(models=[])
    _transport.models.assert_called_once_with()


def test_stats():
    _transport.reset_mock()
    expected = StatsResult.model_validate({"uptime_s": 1.0, "memory": {}, "models": {}})
    _transport.stats.return_value = expected

    assert client.stats() is expected
    _transport.stats.assert_called_once_with()


def test_close():
    _transport.reset_mock()
    client.close()
    _transport.close.assert_called_once_with()


def test_context_manager():
    _transport.reset_mock()
    with client as _:
        pass

    _transport.close.assert_called_once_with()
