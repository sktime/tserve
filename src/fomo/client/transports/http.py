import json
from typing import Any

import httpx

from fomo.client.errors import FoMoError
from fomo.types import HealthResult, ModelsResult, StatsResult
from fomo.types.converters import unpack_envelope

_ARROW_STREAM = "application/vnd.apache.arrow.stream"


class HttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 60.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def forecast(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]:
        response = self._request(
            "POST",
            "/forecast/bytes",
            data={"metadata": json.dumps(metadata)},
            files={
                name: (name, blob, _ARROW_STREAM)
                for name, blob in bytes_encoded.items()
            },
        )
        return unpack_envelope(response.content)

    def health(self) -> HealthResult:
        return HealthResult.model_validate(self._request("GET", "/health").json())

    def models(self) -> ModelsResult:
        return ModelsResult.model_validate(self._request("GET", "/models").json())

    def stats(self) -> StatsResult:
        return StatsResult.model_validate(self._request("GET", "/stats").json())

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
