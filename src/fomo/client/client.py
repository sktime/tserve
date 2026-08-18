from __future__ import annotations

from typing import Any

from fomo.client.transports.http import HttpTransport
from fomo.types import ForecastRequest, ForecastResult, HealthResult, ModelsResult


class Client:
    def __init__(self, url: str, *, timeout: float = 60.0) -> None:
        self._transport = HttpTransport(url, timeout=timeout)

    def forecast(
        self,
        *,
        history: Any,
        time: str,
        target: list[str],
        horizon: int,
        model: str = "dummy",
        future: Any = None,
        static: Any = None,
        series_id: list[str] | None = None,
        known_future: list[str] | None = None,
        past_only: list[str] | None = None,
        freq: str | None = None,
        quantiles: list[float] | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> ForecastResult:
        request = ForecastRequest(
            history=history,
            time=time,
            target=target,
            horizon=horizon,
            model=model,
            future=future,
            static=static,
            series_id=series_id,
            known_future=known_future,
            past_only=past_only,
            freq=freq,
            quantiles=quantiles,
            model_config=model_config,
        )
        return self._transport.forecast(request)

    def health(self) -> HealthResult:
        return self._transport.health()

    def models(self) -> ModelsResult:
        return self._transport.models()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
