import narwhals as nw
import pandas as pd
import pytest

from fomo.runtime.executors.sktime.convertors import from_request, to_response
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


def test_from_request():
    y, X, X_future, fh, quantiles = from_request(_request())

    assert list(y.columns) == ["sales"]
    assert X is None
    assert X_future is None
    assert list(fh) == [1]
    assert quantiles is None


def test_from_request_rejects_panel():
    request = _request(
        series_id=["store"],
        history=_df(store=["A"], timestamp=["2024-01-01"], sales=[120]),
    )

    with pytest.raises(ValueError, match="panel data"):
        from_request(request)


def test_to_response():
    preds = pd.DataFrame(
        {"sales": [120.0]},
        index=pd.DatetimeIndex(["2024-01-02"], name="timestamp"),
    )

    response = to_response(preds, _request())

    assert isinstance(response, CoercedForecastResponse)
    assert isinstance(response.predictions, nw.DataFrame)
    assert response.model == "naive"
    assert response.quantiles is None
