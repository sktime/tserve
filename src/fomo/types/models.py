from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ForecastRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    history: Any
    time: str
    target: list[str]
    horizon: int
    model: str = "dummy"
    future: Any = None
    static: Any = None
    series_id: list[str] | None = None
    known_future: list[str] | None = None
    past_only: list[str] | None = None
    freq: str | None = None
    quantiles: list[float] | None = None
    model_params: dict[str, Any] | None = Field(default=None, alias="model_config")


class ForecastResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    predictions: Any
    model: str
    request_id: str
    quantiles: Any = None


class HealthError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: str
    message: str


class HealthResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alias: str
    estimator: str
    executor: str
    multivariate: bool
    exogenous: bool
    quantiles: bool


class ModelsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    error: str
    code: str
    request_id: str
    details: dict[str, Any] | None = None
