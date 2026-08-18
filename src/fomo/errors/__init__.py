from __future__ import annotations

from typing import Any

class FoMoError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "internal_error",
        request_id: str = "",
        details: Any = None,
        status_code: int = 500,
    ) -> None:
        self.message = message
        self.code = code
        self.request_id = request_id
        self.details = details
        self.status_code = status_code
        super().__init__(f"{message} [{code}]")


def error_payload(exc: BaseException, request_id: str) -> tuple[int, dict[str, Any]]:
    if isinstance(exc, ValueError):
        status, code = 400, "bad_request"
    elif isinstance(exc, RuntimeError):
        status, code = 503, "model_unavailable"
    else:
        status, code = 500, "internal_error"
    return status, {
        "error": str(exc),
        "code": code,
        "request_id": request_id,
    }


def error_from_response(body: Any, status_code: int) -> FoMoError:
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if not isinstance(detail, dict):
        return FoMoError(str(detail), code="http_error", status_code=status_code)
    return FoMoError(
        str(detail.get("error", detail)),
        code=str(detail.get("code", "http_error")),
        request_id=str(detail.get("request_id", "")),
        details=detail.get("details"),
        status_code=status_code,
    )
