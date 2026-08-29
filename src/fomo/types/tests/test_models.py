import re

import narwhals as nw
import pytest
from pydantic import ValidationError

from fomo.types._checks import _TABLE_SHAPE
from fomo.types._examples import (
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
        "past": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
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
        "past": _df(timestamp=["2024-01-01"], sales=[120]),
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
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
            {"past": 123},
            rf"past must be {re.escape(_TABLE_SHAPE)}, got int",
            id="past_not_a_frame",
        ),
        pytest.param(
            {"past": {"timestamp": "2024-01-01"}},
            r"past column values must be lists, got \{'timestamp': 'str'\}",
            id="past_invalid_dict",
        ),
        pytest.param(
            {"future": [1, 2]},
            rf"future must be {re.escape(_TABLE_SHAPE)}, got list",
            id="future_not_a_frame",
        ),
        pytest.param(
            {"static": {"store": "A"}},
            r"static column values must be lists, got \{'store': 'str'\}",
            id="static_invalid_dict",
        ),
        pytest.param(
            {"fh": 0},
            "Input should be greater than 0",
            id="fh_zero",
        ),
        pytest.param(
            {"fh": -1},
            "Input should be greater than 0",
            id="fh_negative",
        ),
        pytest.param(
            {"target": []},
            "List should have at least 1 item",
            id="target_empty",
        ),
        pytest.param(
            {
                "past": {
                    "columns": ["timestamp", "sales"],
                    "data": [["2024-01-01", 120], ["2024-01-02"]],
                }
            },
            r"past\['data'\] row 1 has 1 values, expected 2 for columns",
            id="past_row_length_mismatch",
        ),
        pytest.param(
            {
                "past": {
                    "columns": ["timestamp", "sales"],
                    "data": [["2024-01-01", 120]],
                    "index": [0],
                }
            },
            r"past has extra keys \['index'\]; use only 'columns' and 'data', "
            r"or a column-oriented dict",
            id="past_columns_data_extra_keys",
        ),
        pytest.param(
            {"past": {"timestamp": ["2024-01-01", "2024-01-02"], "sales": [120]}},
            r"past columns must have the same number of rows",
            id="past_unequal_column_lengths",
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
            rf"predictions must be {re.escape(_TABLE_SHAPE)}, got object",
            id="predictions_not_a_frame",
        ),
        pytest.param(
            {"quantiles": {"q": 0.5}},
            r"quantiles column values must be lists, got \{'q': 'float'\}",
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
            r"past is missing columns: \['date'\] \(available:",
            id="past_missing_time_column",
        ),
        pytest.param(
            {"target": ["demand"]},
            r"past is missing columns: \['demand'\]",
            id="past_missing_target_column",
        ),
        pytest.param(
            {"future": _df(price=[8.99])},
            r"future is missing columns: \['timestamp'\]",
            id="future_missing_time_column",
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
            "predictions table has no columns",
            id="predictions_with_no_columns",
        ),
        pytest.param(
            {"quantiles": _df()},
            "quantiles table has no columns",
            id="quantiles_with_no_columns",
        ),
    ],
)
def test_coerced_response_rejects(kwargs, match):
    with pytest.raises(ValidationError, match=match):
        _coerced_response(**kwargs)
