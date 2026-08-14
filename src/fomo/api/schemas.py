from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fomo.runtime.registry import get_model

# Common pandas / sktime offset aliases (see Retrocast freq enum).
Freq = Literal[
    "10S",
    "min",
    "5min",
    "10min",
    "15min",
    "30min",
    "H",
    "D",
    "W",
    "M",
    "Q",
    "Y",
]

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


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str]
    data: list[list[Any]]


class ForecastRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [FORECAST_REQUEST_EXAMPLE]},
    )

    data: Table
    exog_data: Table | None = None
    target_columns: list[str] | None = None
    exog_columns: list[str] | None = None
    time_column: str | None = None
    id_columns: list[str] | None = None
    horizon: int = Field(gt=0, le=10_000)
    freq: Freq | None = None
    context: int | None = Field(default=None, gt=0)
    quantiles: list[float] | None = None
    model_config_overrides: dict[str, Any] | None = Field(default=None, alias="model_config")
    model: str = "dummy"

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
