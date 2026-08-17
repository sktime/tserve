from typing import Protocol

from fomo.runtime.registry import ModelSpec
from fomo.runtime.types import ForecastJob, ForecastResult


class Executor(Protocol):
    def load(self, spec: ModelSpec) -> None: ...

    def predict(self, job: ForecastJob) -> ForecastResult: ...
