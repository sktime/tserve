from __future__ import annotations

from dataclasses import asdict
from typing import Any

import httpx
from pydantic import ValidationError

from fomo.client.errors import FoMoError
from fomo.client.types import (
    ForecastResult,
    HealthError,
    HealthResult,
    ModelInfo,
    ModelsResult,
    Payload,
)
from fomo.contract.wire import ForecastRequest


def _error_message(body: Any) -> tuple[str, str | None]:
    if isinstance(body, dict):
        detail = body.get("detail", body)
        if isinstance(detail, dict):
            message = detail.get("error") or detail.get("msg") or str(detail)
            code = detail.get("code")
            return str(message), code if isinstance(code, str) else None
        if isinstance(detail, list) and detail:
            return str(detail[0]), "validation_error"
        return str(detail), None
    return str(body), None


class HttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 60.0) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def forecast(self, payload: Payload) -> ForecastResult:
        try:
            request = ForecastRequest.model_validate(
                {key: value for key, value in asdict(payload).items() if value is not None}
            )
        except ValidationError as exc:
            raise FoMoError(
                "invalid forecast request",
                code="validation_error",
                details=exc.errors(),
            ) from exc

        body = self._request(
            "POST",
            "/forecast",
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return ForecastResult(
            predictions=body["predictions"],
            model=body["model"],
            request_id=body["request_id"],
            quantiles=body.get("quantiles"),
        )

    def health(self) -> HealthResult:
        body = self._request("GET", "/health")
        err = body.get("error")
        return HealthResult(
            status=body["status"],
            error=(
                HealthError(code=err["code"], message=err["message"])
                if err is not None
                else None
            ),
        )

    def models(self) -> ModelsResult:
        body = self._request("GET", "/models")
        return ModelsResult(
            models=[
                ModelInfo(
                    alias=item["alias"],
                    estimator=item["estimator"],
                    executor=item["executor"],
                    multivariate=item["multivariate"],
                    exogenous=item["exogenous"],
                    quantiles=item["quantiles"],
                )
                for item in body["models"]
            ]
        )

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
            message, code = _error_message(body)
            raise FoMoError(
                message,
                code=code,
                details=body,
            )
        return body
