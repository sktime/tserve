from typing import Protocol

from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


class Executor(Protocol):
    def load(self, info: ModelInfo) -> None: ...

    def predict(self, request: ForecastRequest) -> ForecastResponse: ...
