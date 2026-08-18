from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import narwhals as nw
from pydantic import BaseModel


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


@dataclass(frozen=True)
class ForecastJob:
    model: str
    y: nw.DataFrame
    horizon: int
    target: tuple[str, ...]
    time: str
    series_id: tuple[str, ...] = field(default_factory=tuple)
    X: nw.DataFrame | None = None
    X_future: nw.DataFrame | None = None
    past_only: tuple[str, ...] = field(default_factory=tuple)
    freq: str | None = None
    quantiles: tuple[float, ...] | None = None
    model_config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ForecastResult:
    y_pred: nw.DataFrame
    model: str
    quantiles: nw.DataFrame | None = None


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
