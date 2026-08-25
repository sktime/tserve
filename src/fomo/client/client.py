from typing import Any, Self

from fomo.client.transports.http import HttpTransport
from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult, StatsResult
from fomo.types.converters import coerce_request, encode_request, decode_response


class Client:
    def __init__(
        self,
        url: str,
        *,
        timeout: float = 60.0,
        transport: HttpTransport | None = None,
    ) -> None:
        self._transport = transport or HttpTransport(url, timeout=timeout)

    def forecast(
        self,
        *,
        history: Any,
        time: str,
        target: list[str],
        horizon: int,
        context: int,
        model: str = "naive",
        future: Any = None,
        static: Any = None,
        series_id: list[str] | None = None,
        known_future: list[str] | None = None,
        past_only: list[str] | None = None,
        freq: str | None = None,
        quantiles: list[float] | None = None,
        params: dict[str, Any] | None = None,
    ) -> ForecastResponse:
        request = ForecastRequest(
            history=history,
            time=time,
            target=target,
            horizon=horizon,
            context=context,
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
        coerced = coerce_request(request)

        # 1. encode request to json + bytes
        req_metadata, req_bytes_encoded = encode_request(coerced)
        # 2. send request to transport
        res_metadata, res_bytes_encoded = self._transport.forecast(req_metadata, req_bytes_encoded)
        # 3. decode response to json + bytes
        response = decode_response(res_metadata, res_bytes_encoded)

        if type(history) == dict:
            predictions = response.predictions.to_dict(as_series=False)
            quantile_table = (
                response.quantiles.to_dict(as_series=False)
                if response.quantiles is not None
                else None
            )
        else:
            imp = coerced.history.implementation.value
            predictions = getattr(response.predictions, f"to_{imp}")()
            quantile_table = (
                getattr(response.quantiles, f"to_{imp}")()
                if response.quantiles is not None
                else None
            )

        return ForecastResponse(
            predictions=predictions,
            model=response.model,
            request_id=response.request_id,
            quantiles=quantile_table,
        )

    def health(self) -> HealthResult:
        return self._transport.health()

    def models(self) -> ModelsResult:
        return self._transport.models()

    def stats(self) -> StatsResult:
        return self._transport.stats()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
