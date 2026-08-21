from __future__ import annotations

import json
from email.parser import BytesParser
from email.policy import HTTP
from typing import Any

import httpx

from fomo.client.errors import FoMoError
from fomo.types import HealthResult, ModelsResult


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
            files=bytes_encoded,
        )
        return _read_form(response)

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


def _read_form(response: httpx.Response) -> tuple[dict, dict[str, bytes]]:
    content_type = response.headers.get("content-type", "")
    msg = BytesParser(policy=HTTP).parsebytes(
        b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + response.content
    )
    metadata: dict = {}
    files: dict[str, bytes] = {}
    for part in msg.iter_parts():
        name = part.get_param("name", header="content-disposition")
        payload = part.get_payload(decode=True) or b""
        if name == "response":
            metadata = json.loads(payload.decode())
        elif name:
            files[name] = payload
    return metadata, files
