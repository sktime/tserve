from typing import Any


class FoMoError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "http_error",
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
