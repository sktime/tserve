from typing import Protocol

from fomo.types import HealthResult, ModelsResult, StatsResult


class BaseTransport(Protocol):
    def forecast(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]: ...

    def health(self) -> HealthResult: ...

    def models(self) -> ModelsResult: ...

    def stats(self) -> StatsResult: ...

    def close(self) -> None: ...
