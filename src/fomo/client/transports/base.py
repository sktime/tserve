from __future__ import annotations

from typing import Protocol

from fomo.client.types import ForecastResult, HealthResult, ModelsResult, Payload


class BaseTransport(Protocol):
    def forecast(self, payload: Payload) -> ForecastResult: ...

    def health(self) -> HealthResult: ...

    def models(self) -> ModelsResult: ...

    def close(self) -> None: ...
