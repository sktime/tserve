from __future__ import annotations

from typing import Any

import httpx

from fomo.client.transports.base import TransportResponse


class HttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 60.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def call(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> TransportResponse:
        kwargs: dict[str, Any] = {} if payload is None else {"json": payload}
        response = self._client.request(method, path, **kwargs)
        if response.headers.get("content-type", "").startswith("application/json"):
            body: Any = response.json()
        else:
            body = response.text
        return TransportResponse(response.status_code, body)

    def close(self) -> None:
        self._client.close()
