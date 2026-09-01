import narwhals as nw
import pandas as pd

from fomo.runtime.executors.sktime.converters import from_request, to_response
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


def _request(**kwargs):
    payload = {
        "past": _df(timestamp=["2024-01-01"], sales=[120]),
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return CoercedForecastRequest.model_validate(payload)


def test_from_request():
    y, X, X_future, fh, quantiles = from_request(_request())

    assert list(y.columns) == ["sales"]
    assert y.index.equals(pd.DatetimeIndex(["2024-01-01"], name="timestamp"))
    assert X is None
    assert X_future is None
    assert list(fh.to_pandas()) == [1]
    assert quantiles is None


def test_from_request_keeps_integer_index():
    y, *_ = from_request(_request(past=_df(timestamp=[1, 2, 3], sales=[120, 135, 128])))

    assert y.index.equals(pd.Index([1, 2, 3], name="timestamp"))


def test_from_request_keeps_datetime_index():
    stamps = pd.to_datetime(["2024-01-01", "2024-01-02"])
    y, *_ = from_request(
        _request(past=_df(timestamp=stamps, sales=[120, 135]), fh=1)
    )

    assert y.index.equals(pd.DatetimeIndex(stamps, name="timestamp"))


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
