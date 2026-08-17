from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class TransportResponse:
    status_code: int
    body: Any


class Transport(Protocol):
    def call(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> TransportResponse: ...
