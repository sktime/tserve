from fomo.runtime.executors.plugins import register
from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


@register("pytorch-forecasting")
class PytorchForecastingExecutor:
    def load(self, spec: ModelInfo) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {spec.alias!r})"
        )

    def predict(self, request: ForecastRequest) -> ForecastResponse:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {request.model!r})"
        )
