from __future__ import annotations

from typing import Any

from fomo.client.transports.http import HttpTransport
from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult
from fomo.types.converters import frame_to_format, table_format, table_to_frame


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
        params: dict[str, Any] | None = None,
    ) -> ForecastResponse:
        fmt = table_format(history)
        history = table_to_frame(history)
        future = table_to_frame(future) if future is not None else None
        static = table_to_frame(static) if static is not None else None

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
            params=params,
        )
        response = self._transport.forecast(request)
        response.predictions = frame_to_format(response.predictions, fmt)
        if response.quantiles is not None:
            response.quantiles = frame_to_format(response.quantiles, fmt)
        return response

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
