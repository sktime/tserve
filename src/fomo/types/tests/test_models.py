import pytest

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
    ForecastRequest,
    ForecastResponse,
    HealthResult,
    ModelInfo,
    ModelsResult,
    StatsResult,
)


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
