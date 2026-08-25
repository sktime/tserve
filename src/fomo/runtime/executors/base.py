from abc import ABC, abstractmethod
from typing import Any

from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


class Executor(ABC):
    @abstractmethod
    def load(self, info: ModelInfo, model: Any) -> None: ...

    @abstractmethod
    def warmup(self) -> None: ...

    @abstractmethod
    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse: ...
