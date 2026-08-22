from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from fomo.types.examples import (
    FORECAST_REQUEST,
    FORECAST_RESULT,
    HEALTH_OK,
    MODELS_RESULT,
    STATS_RESULT,
)


class ForecastRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": FORECAST_REQUEST})

    history: Any = None
    time: str
    target: list[str]
    horizon: int
    model: str = "naive"
    future: Any = None
    static: Any = None
    series_id: list[str] | None = None
    known_future: list[str] | None = None
    past_only: list[str] | None = None
    freq: str | None = None
    quantiles: list[float] | None = None
    params: dict[str, Any] | None = None


class ForecastResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": FORECAST_RESULT})

    predictions: Any = None
    model: str
    request_id: str
    quantiles: Any = None


class HealthError(BaseModel):
    code: str
    message: str


class HealthResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": HEALTH_OK})

    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    id: str
    executor: Literal["sktime", "pytorch-forecasting", "custom"]
    source: Literal["object", "registry", "directory"]


class ModelsResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": MODELS_RESULT})

    models: list[ModelInfo]


class MemoryStats(BaseModel):
    cpu_rss_mb: float | None = None
    gpu_mb: float | None = None


class LatencySummary(BaseModel):
    count: int
    total: float
    mean: float | None = None
    fastest: float | None = None
    slowest: float | None = None


class RequestCounts(BaseModel):
    total: int
    ok: int
    failed: int


class ModelStats(BaseModel):
    executor: str | None = None
    load_s: float | None = None
    warmup_s: float | None = None
    requests: RequestCounts
    latency_s: LatencySummary


class StatsResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": STATS_RESULT})

    uptime_s: float
    memory: MemoryStats
    models: dict[str, ModelStats]
