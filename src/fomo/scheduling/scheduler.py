"""Single-threaded scheduler: serializes forecast jobs through the executor."""

from fomo.runtime.executor import Executor
from fomo.runtime.types import ForecastJob, ForecastResult


class Scheduler:
    def __init__(self, executor: Executor) -> None:
        self._executor = executor

    def run(self, job: ForecastJob) -> ForecastResult:
        return self._executor.predict(job)
