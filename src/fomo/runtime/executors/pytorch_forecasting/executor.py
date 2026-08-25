from typing import Any

from fomo.runtime.executors.base import Executor
from fomo.runtime.executors.plugins import register
from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


@register("pytorch-forecasting")
class PytorchForecastingExecutor(Executor):
    def load(self, info: ModelInfo, model: Any) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {info.id!r})"
        )

    def warmup(self) -> None:
        raise NotImplementedError("pytorch-forecasting executor is not implemented yet")

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {request.model!r})"
        )
