from typing import Any

import pandas as pd
from pandas.tseries.frequencies import to_offset
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fomo.runtime.registry import get_model

FORECAST_REQUEST_EXAMPLE = {
    "data": {
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-01", 120],
            ["2024-01-02", 135],
            ["2024-01-03", 128],
            ["2024-01-04", 142],
            ["2024-01-05", 138],
        ],
    },
    "target_columns": ["sales"],
    "time_column": "timestamp",
    "horizon": 3,
    "freq": "D",
    "model": "dummy",
}

FORECAST_RESPONSE_EXAMPLE = {
    "predictions": {
        "columns": ["sales"],
        "data": [[138.0], [138.0], [138.0]],
    },
    "quantiles": None,
    "model": "dummy",
    "request_id": "00000000-0000-0000-0000-000000000000",
}


def _empty_list_to_none(value: list[str] | None) -> list[str] | None:
    if value is not None and len(value) == 0:
        return None
    return value


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str] = Field(min_length=1)
    data: list[list[Any]] = Field(min_length=1)

    @model_validator(mode="after")
    def rows_match_columns(self) -> "Table":
        if len(set(self.columns)) != len(self.columns):
            raise ValueError("duplicate column names")
        width = len(self.columns)
        for i, row in enumerate(self.data):
            if len(row) != width:
                raise ValueError(f"row {i} has {len(row)} values, expected {width}")
        return self

    def require(self, names: list[str], *, label: str) -> None:
        missing = [name for name in names if name not in self.columns]
        if missing:
            raise ValueError(f"{label} missing columns: {missing}")


class ForecastRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [FORECAST_REQUEST_EXAMPLE]},
    )

    history: Table
    future: Table | None = None
    static: Table | None = None
    series_id: list[str] | None = None
    time: str
    target: list[str] = Field(min_length=1)
    known_future: list[str] | None = None
    past_only: list[str] | None = None
    horizon: int = Field(gt=0, le=10_000)
    freq: str | None = None
    quantiles: list[float] | None = None
    model_config_overrides: dict[str, Any] | None = Field(default=None, alias="model_config")
    model: str = "dummy"

    @field_validator("series_id", "known_future", "past_only", mode="before")
    @classmethod
    def omit_empty_role_lists(cls, value: list[str] | None) -> list[str] | None:
        return _empty_list_to_none(value)

    @model_validator(mode="before")
    @classmethod
    def horizon_alias(cls, data: Any) -> Any:
        if isinstance(data, dict) and "fh" in data and "horizon" not in data:
            data = dict(data)
            data["horizon"] = data.pop("fh")
        return data

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

    @field_validator("quantiles")
    @classmethod
    def valid_quantiles(cls, value: list[float] | None) -> list[float] | None:
        if value is None:
            return value
        for q in value:
            if not 0 < q < 1:
                raise ValueError("quantiles must be strictly between 0 and 1")
        return sorted(set(value))


class ForecastResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={"examples": [FORECAST_RESPONSE_EXAMPLE]},
    )

    predictions: Table
    quantiles: Table | None = None
    model: str
    request_id: str


class ModelInfo(BaseModel):
    alias: str
    estimator: str
    multivariate: bool
    exogenous: bool
    quantiles: bool


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    error: str
    code: str
    request_id: str
    details: dict[str, Any] | None = None
