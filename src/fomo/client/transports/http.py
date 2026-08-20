from __future__ import annotations

from typing import Any

import httpx

from fomo.client.errors import FoMoError
from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult
from fomo.types.codec import (
    ARROW_CONTENT_TYPE,
    decode_forecast_response_arrow,
    encode_forecast_arrow,
)


class HttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 60.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def forecast(self, request: ForecastRequest) -> ForecastResponse:
        response = self._request(
            "POST",
            "/forecast",
            content=encode_forecast_arrow(request),
            headers={"Content-Type": ARROW_CONTENT_TYPE},
        )
        content_type = response.headers.get("content-type", "").split(";", 1)[0]
        if content_type != ARROW_CONTENT_TYPE:
            raise ValueError(f"expected {ARROW_CONTENT_TYPE!r}, received {content_type!r}")
        return decode_forecast_response_arrow(response.content)

    def health(self) -> HealthResult:
        return HealthResult.model_validate(self._request("GET", "/health").json())

    def models(self) -> ModelsResult:
        return ModelsResult.model_validate(self._request("GET", "/models").json())

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self._client.request(method, path, **kwargs)
        if response.status_code < 400:
            return response

        if response.headers.get("content-type", "").startswith("application/json"):
            body: Any = response.json()
        else:
            body = response.text
        detail = body.get("detail", body) if isinstance(body, dict) else body
        if isinstance(detail, dict):
            raise FoMoError(
                str(detail.get("error", detail)),
                code=str(detail.get("code", "http_error")),
                request_id=str(detail.get("request_id", "")),
                details=detail.get("details"),
                status_code=response.status_code,
            )
        raise FoMoError(str(detail), status_code=response.status_code)
