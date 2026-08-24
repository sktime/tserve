from typing import Any, Literal, Self

import narwhals as nw
from pydantic import BaseModel, ConfigDict, model_validator

from fomo.types._checks import _check_frame, _require_columns
from fomo.types._examples import (
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
    context: int
    model: str = "naive"
    future: Any = None
    static: Any = None
    series_id: list[str] | None = None
    known_future: list[str] | None = None
    past_only: list[str] | None = None
    freq: str | None = None
    quantiles: list[float] | None = None
    params: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _check_frames(self) -> Self:
        _check_frame(self.history, name="history")
        _check_frame(self.future, name="future")
        _check_frame(self.static, name="static")
        return self


class ForecastResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": FORECAST_RESULT})

    predictions: Any = None
    model: str
    request_id: str
    quantiles: Any = None

    @model_validator(mode="after")
    def _check_frames(self) -> Self:
        _check_frame(self.predictions, name="predictions")
        _check_frame(self.quantiles, name="quantiles")
        return self


class CoercedForecastRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    history: nw.DataFrame[Any]
    time: str
    target: list[str]
    horizon: int
    context: int
    model: str = "naive"
    future: nw.DataFrame[Any] | None = None
    static: nw.DataFrame[Any] | None = None
    series_id: list[str] | None = None
    known_future: list[str] | None = None
    past_only: list[str] | None = None
    freq: str | None = None
    quantiles: list[float] | None = None
    params: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _check_frame_columns(self) -> Self:
        history_cols = [self.time, *self.target]
        if self.series_id:
            history_cols.extend(self.series_id)
        if self.known_future:
            history_cols.extend(self.known_future)
        if self.past_only:
            history_cols.extend(self.past_only)
        _require_columns(self.history, history_cols, frame_name="history")

        if self.known_future and self.future is None:
            raise ValueError("future is required when known_future is set")

        if self.future is not None:
            future_cols = [self.time]
            if self.series_id:
                future_cols.extend(self.series_id)
            if self.known_future:
                future_cols.extend(self.known_future)
            _require_columns(self.future, future_cols, frame_name="future")

        if self.static is not None and self.series_id:
            _require_columns(self.static, self.series_id, frame_name="static")

        return self


class CoercedForecastResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    predictions: nw.DataFrame[Any]
    model: str
    request_id: str
    quantiles: nw.DataFrame[Any] | None = None

    @model_validator(mode="after")
    def _check_frame_columns(self) -> Self:
        if not self.predictions.columns:
            raise ValueError("predictions has no columns")
        if self.quantiles is not None and not self.quantiles.columns:
            raise ValueError("quantiles has no columns")
        return self


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
