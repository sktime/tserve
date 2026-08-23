from fomo.runtime.executors.plugins import register
from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo
from typing import Any


@register("pytorch-forecasting")
class PytorchForecastingExecutor:
    def load(self, info: ModelInfo, model: Any) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {info.id!r})"
        )

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {request.model!r})"
        )
