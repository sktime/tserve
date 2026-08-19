from fomo.runtime.executors.plugins import register
from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


@register("pytorch-forecasting")
class PytorchForecastingExecutor:
    def load(self, info: ModelInfo) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {info.alias!r})"
        )

    def predict(self, request: ForecastRequest) -> ForecastResponse:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {request.model!r})"
        )
