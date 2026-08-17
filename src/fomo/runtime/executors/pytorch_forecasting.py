from fomo.runtime.executors.plugins import register
from fomo.runtime.registry import ModelSpec
from fomo.runtime.types import ForecastJob, ForecastResult


@register("pytorch-forecasting")
class PytorchForecastingExecutor:
    def load(self, spec: ModelSpec) -> None:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {spec.alias!r})"
        )

    def predict(self, job: ForecastJob) -> ForecastResult:
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {job.model!r})"
        )
