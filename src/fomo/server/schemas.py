from pandas.tseries.frequencies import to_offset
from pydantic import field_validator

from fomo.contract.wire import (
    FORECAST_REQUEST_EXAMPLE,
    FORECAST_RESPONSE_EXAMPLE,
    ErrorResponse,
    ForecastRequest as WireForecastRequest,
    ForecastResponse,
    ModelInfo,
    ModelsResponse,
    Table,
)
from fomo.runtime.registry import get_model

__all__ = [
    "FORECAST_REQUEST_EXAMPLE",
    "FORECAST_RESPONSE_EXAMPLE",
    "ErrorResponse",
    "ForecastRequest",
    "ForecastResponse",
    "ModelInfo",
    "ModelsResponse",
    "Table",
]


class ForecastRequest(WireForecastRequest):
    @field_validator("model")
    @classmethod
    def known_model(cls, value: str) -> str:
        get_model(value)
        return value

    @field_validator("freq")
    @classmethod
    def valid_freq(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            to_offset(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid freq {value!r}") from exc
        return value
