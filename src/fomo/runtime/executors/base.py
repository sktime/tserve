from typing import Protocol

from fomo.runtime.types import ForecastJob, ForecastResult
from fomo.types import ModelInfo


class Executor(Protocol):
    def load(self, spec: ModelInfo) -> None: ...

    def predict(self, job: ForecastJob) -> ForecastResult: ...
