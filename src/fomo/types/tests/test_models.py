import narwhals as nw
import pytest
from pydantic import ValidationError

from fomo.types.examples import (
    FORECAST_REQUEST,
    FORECAST_RESULT,
    HEALTH_OK,
    HEALTH_UNHEALTHY,
    MODEL_INFO,
    MODELS_RESULT,
    STATS_RESULT,
)
from fomo.types.models import (
    CoercedForecastRequest,
    CoercedForecastResponse,
    ForecastRequest,
    ForecastResponse,
    HealthResult,
    ModelInfo,
    ModelsResult,
    StatsResult,
)


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


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


def _coerced_request(**kwargs):
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


def _coerced_response(**kwargs):
    payload = {
        "predictions": _df(timestamp=["2024-01-02"], sales=[120.0]),
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return CoercedForecastResponse.model_validate(payload)


@pytest.mark.parametrize(
    ("example", "model"),
    [
        (FORECAST_REQUEST, ForecastRequest),
        (FORECAST_RESULT, ForecastResponse),
        (HEALTH_OK, HealthResult),
        (HEALTH_UNHEALTHY, HealthResult),
        (MODEL_INFO, ModelInfo),
        (MODELS_RESULT, ModelsResult),
        (STATS_RESULT, StatsResult),
    ],
)
def test_example_validates_against_model(example, model):
    parsed = model.model_validate(example)
    assert isinstance(parsed, model)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        pytest.param(
            {"history": 123},
            r"history must be a supported dataframe or dict\[str, list\], got int",
            id="history_not_a_frame",
        ),
        pytest.param(
            {"history": {"timestamp": "2024-01-01"}},
            r"history must be dict\[str, list\]",
            id="history_invalid_dict",
        ),
        pytest.param(
            {"future": [1, 2]},
            r"future must be a supported dataframe or dict\[str, list\], got list",
            id="future_not_a_frame",
        ),
        pytest.param(
            {"static": {"store": "A"}},
            r"static must be dict\[str, list\]",
            id="static_invalid_dict",
        ),
    ],
)
def test_forecast_request_rejects(kwargs, match):
    with pytest.raises(ValidationError, match=match):
        _request(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        pytest.param(
            {"predictions": object()},
            r"predictions must be a supported dataframe or dict\[str, list\], got object",
            id="predictions_not_a_frame",
        ),
        pytest.param(
            {"quantiles": {"q": 0.5}},
            r"quantiles must be dict\[str, list\]",
            id="quantiles_invalid_dict",
        ),
    ],
)
def test_forecast_response_rejects(kwargs, match):
    with pytest.raises(ValidationError, match=match):
        _response(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        pytest.param(
            {"time": "date"},
            r"history is missing columns: \['date'\]",
            id="history_missing_time_column",
        ),
        pytest.param(
            {"target": ["demand"]},
            r"history is missing columns: \['demand'\]",
            id="history_missing_target_column",
        ),
        pytest.param(
            {"series_id": ["store"]},
            r"history is missing columns: \['store'\]",
            id="history_missing_series_id_column",
        ),
        pytest.param(
            {"known_future": ["price"], "future": _df(timestamp=["2024-01-02"])},
            r"history is missing columns: \['price'\]",
            id="history_missing_known_future_column",
        ),
        pytest.param(
            {"past_only": ["promo"]},
            r"history is missing columns: \['promo'\]",
            id="history_missing_past_only_column",
        ),
        pytest.param(
            {
                "history": _df(timestamp=["2024-01-01"], sales=[120], price=[9.99]),
                "known_future": ["price"],
            },
            "future is required when known_future is set",
            id="known_future_without_future_frame",
        ),
        pytest.param(
            {
                "history": _df(timestamp=["2024-01-01"], sales=[120], price=[9.99]),
                "known_future": ["price"],
                "future": _df(price=[8.99]),
            },
            r"future is missing columns: \['timestamp'\]",
            id="future_missing_time_column",
        ),
        pytest.param(
            {
                "history": _df(store=["A"], timestamp=["2024-01-01"], sales=[120]),
                "series_id": ["store"],
                "future": _df(timestamp=["2024-01-02"]),
            },
            r"future is missing columns: \['store'\]",
            id="future_missing_series_id_column",
        ),
        pytest.param(
            {
                "history": _df(timestamp=["2024-01-01"], sales=[120], price=[9.99]),
                "known_future": ["price"],
                "future": _df(timestamp=["2024-01-02"]),
            },
            r"future is missing columns: \['price'\]",
            id="future_missing_known_future_column",
        ),
        pytest.param(
            {
                "history": _df(store=["A"], timestamp=["2024-01-01"], sales=[120]),
                "series_id": ["store"],
                "static": _df(store_type=["urban"]),
            },
            r"static is missing columns: \['store'\]",
            id="static_missing_series_id_column",
        ),
    ],
)
def test_coerced_request_rejects(kwargs, match):
    with pytest.raises(ValidationError, match=match):
        _coerced_request(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        pytest.param(
            {"predictions": _df()},
            "predictions has no columns",
            id="predictions_with_no_columns",
        ),
        pytest.param(
            {"quantiles": _df()},
            "quantiles has no columns",
            id="quantiles_with_no_columns",
        ),
    ],
)
def test_coerced_response_rejects(kwargs, match):
    with pytest.raises(ValidationError, match=match):
        _coerced_response(**kwargs)
