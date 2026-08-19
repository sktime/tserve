from fomo.runtime.executors import Executor
from fomo.types.models import ForecastJob, ForecastResult


class Scheduler:
    def __init__(self, executors: dict[str, Executor]) -> None:
        self._executors = executors

    def run(self, job: ForecastJob) -> ForecastResult:
        executor = self._executors.get(job.model)
        if executor is None:
            raise RuntimeError(f"model {job.model!r} is not loaded on this server")
        return executor.predict(job)
