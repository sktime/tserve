from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
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
    params: dict[str, Any] | None = None


class ForecastResponse(BaseModel):
    predictions: Any
    model: str
    request_id: str
    quantiles: Any = None


class ForecastJob(BaseModel):
    model: str
    y: Any
    horizon: int
    target: tuple[str, ...]
    time: str
    series_id: tuple[str, ...] = ()
    X: Any = None
    X_future: Any = None
    past_only: tuple[str, ...] = ()
    freq: str | None = None
    quantiles: tuple[float, ...] | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ForecastResult(BaseModel):
    y_pred: Any
    model: str
    quantiles: Any = None


class HealthError(BaseModel):
    code: str
    message: str


class HealthResult(BaseModel):
    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    alias: str
    estimator: str
    executor: str
    multivariate: bool
    exogenous: bool
    quantiles: bool
    spec: str


class ModelsResult(BaseModel):
    models: list[ModelInfo]
