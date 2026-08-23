from typing import Any, Protocol

from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


class Executor(Protocol):
    def load(self, info: ModelInfo, model: Any) -> None: ...

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse: ...
