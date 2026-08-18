from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Payload:
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
    model_config: dict[str, Any] | None = None


@dataclass
class ForecastResult:
    predictions: Any
    model: str
    request_id: str
    quantiles: Any = None


@dataclass
class HealthError:
    code: str
    message: str


@dataclass
class HealthResult:
    status: str
    error: HealthError | None = None


@dataclass
class ModelInfo:
    alias: str
    estimator: str
    executor: str
    multivariate: bool
    exogenous: bool
    quantiles: bool


@dataclass
class ModelsResult:
    models: list[ModelInfo]
