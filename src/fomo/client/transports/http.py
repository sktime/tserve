from __future__ import annotations

from typing import Any

import httpx

from fomo.errors import error_from_response
from fomo.types import ForecastRequest, ForecastResult, HealthResult, ModelsResult


class HttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 60.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def forecast(self, request: ForecastRequest) -> ForecastResult:
        body = self._request(
            "POST",
            "/forecast",
            json=request.model_dump(mode="json", exclude_none=True),
        )
        return ForecastResult.model_validate(body)

    def health(self) -> HealthResult:
        return HealthResult.model_validate(self._request("GET", "/health"))

    def models(self) -> ModelsResult:
        return ModelsResult.model_validate(self._request("GET", "/models"))

    def close(self) -> None:
        self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {} if json is None else {"json": json}
        response = self._client.request(method, path, **kwargs)
        if response.headers.get("content-type", "").startswith("application/json"):
            body: Any = response.json()
        else:
            body = response.text

        if response.status_code >= 400:
            raise error_from_response(body, response.status_code)
        return body
