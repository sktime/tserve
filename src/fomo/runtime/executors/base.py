from typing import Any, Protocol

from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


class Executor(Protocol):
    def load(self, info: ModelInfo, model: Any) -> None: ...

    def predict(self, request: ForecastRequest) -> ForecastResponse: ...
