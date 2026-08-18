from __future__ import annotations

from typing import Any


class FoMoError(Exception):
    """Raised when a FoMo client operation fails (bad input, server error, or transport failure)."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self._format())

    def _format(self) -> str:
        if self.code:
            return f"{self.message} [{self.code}]"
        return self.message
