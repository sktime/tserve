from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

FORECAST_REQUEST_EXAMPLE = {
    "time": "timestamp",
    "target": ["sales"],
    "history": {
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-01", 120],
            ["2024-01-02", 135],
            ["2024-01-03", 128],
            ["2024-01-04", 142],
            ["2024-01-05", 138],
        ],
    },
    "horizon": 3,
    "freq": "D",
    "model": "dummy",
}

FORECAST_RESPONSE_EXAMPLE = {
    "predictions": {
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-06T00:00:00", 138.0],
            ["2024-01-07T00:00:00", 138.0],
            ["2024-01-08T00:00:00", 138.0],
        ],
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

    @field_validator("quantiles")
    @classmethod
    def valid_quantiles(cls, value: list[float] | None) -> list[float] | None:
        if value is None:
            return value
        for q in value:
            if not 0 < q < 1:
                raise ValueError("quantiles must be strictly between 0 and 1")
        return sorted(set(value))

    @model_validator(mode="after")
    def enforce_contract(self) -> "ForecastRequest":
        roles = {
            "time": [self.time],
            "target": self.target,
            "series_id": self.series_id or [],
            "known_future": self.known_future or [],
            "past_only": self.past_only or [],
        }
        seen: dict[str, str] = {}
        for role, names in roles.items():
            if len(set(names)) != len(names):
                raise ValueError(f"{role} has duplicate names")
            for name in names:
                other = seen.get(name)
                if other is not None:
                    raise ValueError(f"column {name!r} is listed in both {other} and {role}")
                seen[name] = role

        self.history.require(
            [*roles["series_id"], self.time, *self.target, *roles["known_future"], *roles["past_only"]],
            label="history",
        )

        if self.known_future is not None and self.future is None:
            raise ValueError("future is required when known_future is set")
        if self.future is not None and self.known_future is None:
            raise ValueError("future requires known_future")

        if self.future is not None:
            assert self.known_future is not None
            self.future.require(
                [*roles["series_id"], self.time, *self.known_future],
                label="future",
            )
            leaked = [name for name in (*self.target, *roles["past_only"]) if name in self.future.columns]
            if leaked:
                raise ValueError(f"future must not contain {leaked}")
            _validate_future_horizon(self)

        if self.static is not None:
            if self.series_id is None:
                raise ValueError("series_id is required when static is set")
            self.static.require(self.series_id, label="static")
            features = [name for name in self.static.columns if name not in self.series_id]
            extra = [name for name in features if name in seen]
            if extra:
                raise ValueError(f"static columns collide with other roles: {extra}")
            if not features:
                raise ValueError("static must include at least one feature column")
            _validate_static_keys(self)

        return self


def _key_tuples(table: Table, keys: list[str]) -> list[tuple[Any, ...]]:
    idx = [table.columns.index(key) for key in keys]
    return [tuple(row[i] for i in idx) for row in table.data]


def _validate_future_horizon(request: ForecastRequest) -> None:
    future = request.future
    assert future is not None
    keys = request.series_id or []
    if not keys:
        if len(future.data) != request.horizon:
            raise ValueError(
                f"future has {len(future.data)} rows, expected horizon={request.horizon}"
            )
        _validate_future_after_history(request, [()])
        return

    hist_keys = set(_key_tuples(request.history, keys))
    fut_keys = _key_tuples(future, keys)
    fut_set = set(fut_keys)
    if hist_keys != fut_set:
        raise ValueError("future series_id values must match history")

    counts: dict[tuple[Any, ...], int] = {}
    for key in fut_keys:
        counts[key] = counts.get(key, 0) + 1
    bad = {key: n for key, n in counts.items() if n != request.horizon}
    if bad:
        raise ValueError(
            f"each series must have exactly {request.horizon} future rows, got {bad}"
        )
    _validate_future_after_history(request, list(hist_keys))


def _validate_future_after_history(
    request: ForecastRequest, series_keys: list[tuple[Any, ...]]
) -> None:
    future = request.future
    assert future is not None
    keys = request.series_id or []
    hist_times = _last_times(request.history, keys, request.time)
    fut_times = _column_by_key(future, keys, request.time)
    for key in series_keys:
        last = hist_times[key]
        first_future = min(fut_times[key])
        if not _time_after(first_future, last):
            label = key if keys else "series"
            raise ValueError(f"future timestamps for {label} must be after the last history time")


def _last_times(table: Table, keys: list[str], time: str) -> dict[tuple[Any, ...], Any]:
    times = _column_by_key(table, keys, time)
    return {key: max(values) for key, values in times.items()}


def _column_by_key(table: Table, keys: list[str], column: str) -> dict[tuple[Any, ...], list[Any]]:
    col_i = table.columns.index(column)
    key_idx = [table.columns.index(key) for key in keys]
    grouped: dict[tuple[Any, ...], list[Any]] = {}
    for row in table.data:
        key = tuple(row[i] for i in key_idx)
        grouped.setdefault(key, []).append(row[col_i])
    return grouped


def _as_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _time_after(later: Any, earlier: Any) -> bool:
    try:
        return _as_datetime(later) > _as_datetime(earlier)
    except (ValueError, TypeError):
        return later > earlier


def _validate_static_keys(request: ForecastRequest) -> None:
    static = request.static
    assert static is not None and request.series_id is not None
    hist_keys = set(_key_tuples(request.history, request.series_id))
    stat_keys = _key_tuples(static, request.series_id)
    if len(stat_keys) != len(set(stat_keys)):
        raise ValueError("static must have one row per series")
    if set(stat_keys) != hist_keys:
        raise ValueError("static series_id values must match history")


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
    executor: str
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
