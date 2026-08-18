from __future__ import annotations

from typing import Protocol

from fomo.types import ForecastRequest, ForecastResult, HealthResult, ModelsResult


class BaseTransport(Protocol):
    def forecast(self, request: ForecastRequest) -> ForecastResult: ...

    def health(self) -> HealthResult: ...

    def models(self) -> ModelsResult: ...

    def close(self) -> None: ...
