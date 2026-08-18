from fomo.runtime.executors.plugins import register
from fomo.runtime.types import ForecastJob, ForecastResponse
from fomo.types import ModelInfo


@register("pytorch-forecasting")
class PytorchForecastingExecutor:
    def load(self, spec: ModelInfo) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {spec.alias!r})"
        )

    def predict(self, job: ForecastJob) -> ForecastResponse:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {job.model!r})"
        )
