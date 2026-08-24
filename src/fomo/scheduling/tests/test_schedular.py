from unittest.mock import MagicMock

import narwhals as nw
import pytest

from fomo.logging.stats import Stats
from fomo.scheduling.scheduler import Scheduler
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


def _request(**kwargs):
    payload = {
        "history": _df(timestamp=["2024-01-01"], sales=[120]),
        "time": "timestamp",
        "target": ["sales"],
        "horizon": 1,
        "context": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return CoercedForecastRequest.model_validate(payload)


def _response(**kwargs):
    payload = {
        "predictions": _df(timestamp=["2024-01-02"], sales=[120.0]),
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return CoercedForecastResponse.model_validate(payload)


def test_run():
    response = _response()
    executor = MagicMock()
    executor.predict.return_value = response
    stats = Stats()
    stats.register("naive", "sktime", 1.0, 0.5)
    request = _request()

    result = Scheduler({"naive": executor}, stats).run(request)

    assert result is response
    executor.predict.assert_called_once_with(request)
    assert stats.snapshot()["models"]["naive"]["requests"] == {
        "total": 1,
        "ok": 1,
        "failed": 0,
    }


def test_run_rejects_unloaded_model():
    with pytest.raises(RuntimeError, match="model 'naive' is not loaded on this server"):
        Scheduler({}, Stats()).run(_request())
