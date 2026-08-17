from __future__ import annotations

from typing import Any

from fomo.client.transports.base import Transport, TransportResponse
from fomo.client.transports.http import HttpTransport
from fomo.contract.wire import ForecastRequest, ForecastResponse, ModelsResponse


class FoMoError(Exception):
    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class Client:
    def __init__(
        self,
        url: str | None = None,
        *,
        transport: Transport | None = None,
        server: Any | None = None,
        runtime: Any | None = None,
        timeout: float = 60.0,
    ) -> None:
        chosen = [url, transport, server, runtime]
        if sum(value is not None for value in chosen) != 1:
            raise TypeError("provide exactly one of url, transport, server, or runtime")
        if transport is not None:
            self._transport = transport
        elif url is not None:
            self._transport = HttpTransport(url, timeout=timeout)
        else:
            from fomo.client.transports.inprocess import InProcessTransport

            self._transport = InProcessTransport(server.runtime if server is not None else runtime)

    def forecast(
        self,
        request: ForecastRequest | dict[str, Any] | None = None,
        **fields: Any,
    ) -> ForecastResponse:
        if request is not None and fields:
            raise TypeError("pass a request object or keyword fields, not both")
        if isinstance(request, ForecastRequest):
            payload = request.model_dump(mode="json", by_alias=True, exclude_none=True)
        else:
            payload = dict(request or fields)
        return ForecastResponse.model_validate(self._call("POST", "/forecast", payload))

    def health(self) -> dict[str, Any]:
        return self._call("GET", "/health")

    def models(self) -> ModelsResponse:
        return ModelsResponse.model_validate(self._call("GET", "/models"))

    def close(self) -> None:
        closer = getattr(self._transport, "close", None)
        if closer is not None:
            closer()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        response: TransportResponse = self._transport.call(method, path, payload)
        if response.status_code >= 400:
            raise FoMoError(str(response.body), status_code=response.status_code)
        return response.body
