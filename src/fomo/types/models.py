from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class ForecastRequest(BaseModel):
    history: Any = None
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
    predictions: Any = None
    model: str
    request_id: str
    quantiles: Any = None


class HealthError(BaseModel):
    code: str
    message: str


class HealthResult(BaseModel):
    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    alias: str
    executor: Literal["sktime", "pytorch-forecasting", "custom"]
    source: Literal["object", "registry", "directory"]


class ModelsResult(BaseModel):
    models: list[ModelInfo]
