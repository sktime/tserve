import narwhals as nw
import pandas as pd
import pytest

from tserve.runtime.executors.sktime.converters import from_request, to_response
from tserve.types.models import CoercedPredictRequest, CoercedPredictResponse


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


# A datetime index needs three regularly spaced rows for pandas to infer a
# frequency, which the forecasting horizon needs to place future timestamps.
_STAMPS = ["2024-01-01", "2024-01-02", "2024-01-03"]


def _request(**kwargs):
    payload = {
        "past": _df(timestamp=_STAMPS, sales=[120, 135, 128]),
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return CoercedPredictRequest.model_validate(payload)


def test_from_request():
    y, X, X_future, fh, quantiles = from_request(_request())

    assert list(y.columns) == ["sales"]
    assert y.index.equals(pd.DatetimeIndex(_STAMPS, name="timestamp"))
    assert X is None
    assert X_future is None
    assert list(fh.to_pandas()) == [1]
    assert quantiles is None


def test_from_request_horizon_carries_past_frequency():
    """``fh`` needs the frequency; ``past.index[-1:]`` is too short to carry it."""
    _, _, _, fh, _ = from_request(_request())

    assert fh.freq == "D"


def test_from_request_static_broadcasts_over_inferred_future():
    _, X, X_future, _, _ = from_request(_request(fh=2, static=_df(store=["urban"])))

    assert X is not None
    assert X_future is not None
    assert list(X.columns) == ["store"]
    assert set(X["store"]) == {"urban"}
    assert X_future.index.equals(
        pd.DatetimeIndex(["2024-01-04", "2024-01-05"], name="timestamp")
    )


def test_from_request_keeps_integer_index():
    y, *_ = from_request(_request(past=_df(timestamp=[1, 2, 3], sales=[120, 135, 128])))

    assert y.index.equals(pd.Index([1, 2, 3], name="timestamp"))


def test_from_request_keeps_datetime_index():
    stamps = pd.to_datetime(_STAMPS)
    y, *_ = from_request(
        _request(past=_df(timestamp=stamps, sales=[120, 135, 128]), fh=1)
    )

    assert y.index.equals(pd.DatetimeIndex(stamps, name="timestamp"))


@pytest.mark.parametrize(
    ("past", "match"),
    [
        (_df(timestamp=["2024-01-01"], sales=[120]), "could not infer how far apart"),
        (
            _df(timestamp=["2024-01-01", "2024-01-05", "2024-01-19"], sales=[1, 2, 3]),
            "could not infer how far apart",
        ),
        (
            _df(timestamp=["2024-01-01", "2024-01-02", "2024-01-02"], sales=[1, 2, 3]),
            "duplicate timestamp",
        ),
        (
            _df(timestamp=["2024-01-03", "2024-01-01", "2024-01-02"], sales=[1, 2, 3]),
            "not sorted in increasing order",
        ),
        (
            _df(timestamp=["2024-01-01", "", "2024-01-03"], sales=[1, 2, 3]),
            "missing timestamp",
        ),
        (
            _df(timestamp=["not-a-date", "also-not", "nope"], sales=[1, 2, 3]),
            "could not be read as timestamps",
        ),
    ],
)
def test_from_request_rejects_unusable_time_index(past, match):
    with pytest.raises(ValueError, match=match):
        from_request(_request(past=past))


def test_from_request_rejects_empty_static():
    with pytest.raises(ValueError, match="no rows"):
        from_request(_request(static=_df(store=[])))


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        pytest.param(
            {"past": _df(timestamp=[], sales=[])},
            "no rows to forecast from",
            id="empty_past",
        ),
        pytest.param(
            {"past": _df(timestamp=_STAMPS, sales=["1", "2", "3"])},
            "not numeric",
            id="string_numbers",
        ),
        pytest.param(
            {
                "past": _df(
                    timestamp=_STAMPS, sales=[1, 2, 3], region=["EU", "US", "EU"]
                ),
                "target": ["sales", "region"],
            },
            "not numeric",
            id="string_column_as_target",
        ),
        pytest.param(
            {"past": _df(timestamp=_STAMPS, sales=[True, False, True])},
            "not numeric",
            id="boolean_target",
        ),
        pytest.param(
            {
                "past": _df(timestamp=_STAMPS, sales=[1, 2, 3]),
                "time": "sales",
                "target": ["timestamp"],
            },
            "not numeric",
            id="time_points_at_value_column",
        ),
    ],
)
def test_from_request_rejects_unusable_target(kwargs, match):
    with pytest.raises(ValueError, match=match):
        from_request(_request(**kwargs))


def test_from_request_allows_irregular_integer_index():
    """Integer indexes are positional, so they need no inferred frequency."""
    y, *_ = from_request(_request(past=_df(timestamp=[0, 5, 19], sales=[1, 2, 3])))

    assert y.index.equals(pd.Index([0, 5, 19], name="timestamp"))


def test_from_request_passes_shared_columns_as_exogenous():
    """A non-target column in both past and future becomes a covariate."""
    _, X, X_future, _, _ = from_request(
        _request(
            fh=1,
            past=_df(timestamp=_STAMPS, sales=[120, 135, 128], promo=[0, 1, 0]),
            future=_df(timestamp=["2024-01-04"], promo=[1]),
            target=["sales"],
        )
    )

    assert X is not None
    assert X_future is not None
    assert list(X.columns) == ["promo"]
    assert list(X_future.columns) == ["promo"]
    assert X_future["promo"].tolist() == [1]


def test_from_request_combines_covariates_and_static():
    _, X, X_future, _, _ = from_request(
        _request(
            fh=1,
            past=_df(timestamp=_STAMPS, sales=[120, 135, 128], promo=[0, 1, 0]),
            future=_df(timestamp=["2024-01-04"], promo=[1]),
            target=["sales"],
            static=_df(store=["urban"]),
        )
    )

    assert X is not None
    assert X_future is not None
    assert list(X.columns) == ["promo", "store"]
    assert list(X_future.columns) == ["promo", "store"]


def test_from_request_trims_future_to_the_horizon():
    """Future rows beyond ``fh`` are dropped so X_future matches the horizon."""
    _, _, X_future, _, _ = from_request(
        _request(
            fh=1,
            past=_df(timestamp=_STAMPS, sales=[120, 135, 128], promo=[0, 1, 0]),
            future=_df(timestamp=["2024-01-04", "2024-01-05"], promo=[1, 0]),
            target=["sales"],
        )
    )

    assert X_future is not None
    assert X_future.index.equals(pd.DatetimeIndex(["2024-01-04"], name="timestamp"))


def test_from_request_rejects_future_that_misses_the_horizon():
    with pytest.raises(ValueError, match="timestamp\\(s\\) being forecast"):
        from_request(
            _request(
                fh=1,
                past=_df(timestamp=_STAMPS, sales=[120, 135, 128], promo=[0, 1, 0]),
                future=_df(timestamp=["2024-02-01"], promo=[1]),
                target=["sales"],
            )
        )


def test_from_request_ignores_columns_missing_from_either_frame():
    """Exogenous use needs history and future values, so one-sided columns drop."""
    _, X, X_future, _, _ = from_request(
        _request(
            fh=1,
            past=_df(timestamp=_STAMPS, sales=[120, 135, 128], past_only=[1, 2, 3]),
            future=_df(timestamp=["2024-01-04"], future_only=[9]),
            target=["sales"],
        )
    )

    assert X is None
    assert X_future is None


def test_from_request_validates_the_future_index():
    """The future index is checked even when it carries no covariate."""
    with pytest.raises(ValueError, match="not sorted in increasing order"):
        from_request(
            _request(
                fh=2,
                future=_df(timestamp=["2024-01-05", "2024-01-04"]),
                static=_df(store=["urban"]),
            )
        )


def test_to_response():
    preds = pd.DataFrame(
        {"sales": [120.0]},
        index=pd.DatetimeIndex(["2024-01-02"], name="timestamp"),
    )

    response = to_response(preds, _request())

    assert isinstance(response, CoercedPredictResponse)
    assert isinstance(response.predictions, nw.DataFrame)
    assert response.model == "naive"
    assert response.quantiles is None
