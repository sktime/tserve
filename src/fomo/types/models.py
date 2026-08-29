"""Pydantic schemas for forecast requests, responses, and server status.

User-facing models accept flexible native frames. Coerced models hold
narwhals DataFrames and enforce column contracts. Health, model listing,
and stats models describe ``GET /health``, ``GET /models``, and
``GET /stats``.

``HealthError`` is a JSON payload nested under ``HealthResult.error``,
not an exception class. FoMo has no custom exception hierarchy.
Validators raise ``ValueError``; Pydantic constructors expose that as
``ValidationError``.

Notes
-----
Panel (multi-series) input is not supported. The sktime converter
``from_request`` maps a single series from ``past``, ``time``, and
``target``.

See Also
--------
fomo.types.converters
    Turn ``ForecastRequest`` into ``CoercedForecastRequest`` and pack
    frames as Arrow IPC for the bytes path.
fomo.types._checks
    Shape checks run when constructing user-facing forecast models.
"""

from typing import Any, Literal, Self

import narwhals as nw
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fomo.types._checks import _check_frame, _require_columns
from fomo.types._examples import (
    FORECAST_REQUEST,
    FORECAST_RESULT,
    HEALTH_OK,
    MODELS_RESULT,
    STATS_RESULT,
)


class ForecastRequest(BaseModel):
    """User-facing forecast input with native-typed tables.

    This is what JSON ``POST /forecast`` and ``Client.forecast`` accept.
    Frames may be pandas-like, polars, a pyarrow Table, a narwhals
    DataFrame, a column dict (name → list), or a row matrix
    ``{"columns": [...], "data": [[...], ...]}``. Construction only
    checks table *shape* via ``_check_frame``. Column names are
    enforced after coercion on ``CoercedForecastRequest``.

    ``model`` is a **loaded model id** (registry id, zip stem, or the
    id passed with an in-process forecaster), not an executor name
    such as ``"sktime"``.

    Attributes
    ----------
    past : any
        Past observations. Construction only checks table shape.
        After coercion the frame must include ``time`` and every
        ``target``.
    time : str
        Name of the time-index column in ``past`` / ``future`` /
        predictions.
    target : list of str
        One or more target column names (``min_length=1``).
    fh : int
        Number of forecast steps ahead (must be ``> 0``).
    model : str, default ``"naive"``
        Id of a model loaded on this server (see ``GET /models``).
    future : any, optional
        Future rows for known covariates.
    static : any, optional
        Per-series (or single-row) static features. Broadcast over time
        is an executor concern, not this schema.
    quantiles : list of float, optional
        Quantile alphas. When set, executors that support them return a
        quantile table; column naming is executor-specific.

    Raises
    ------
    ValidationError
        If ``past``, ``future``, or ``static`` is not a supported
        table shape (or ``None`` for the optional frames); if
        ``target`` has fewer than one name; if ``fh <= 0``; or if
        other field types fail. Inner validators raise ``ValueError``,
        which Pydantic wraps.

    See Also
    --------
    CoercedForecastRequest
        Internal narwhals form executors consume.
    fomo.types.converters.coerce_request
        Converts this model into ``CoercedForecastRequest``.
    """

    model_config = ConfigDict(json_schema_extra={"example": FORECAST_REQUEST})

    past: Any
    time: str
    target: list[str] = Field(min_length=1)
    fh: int = Field(gt=0)
    model: str = "naive"
    future: Any = None
    static: Any = None
    quantiles: list[float] | None = None

    @model_validator(mode="after")
    def _check_frames(self) -> Self:
        """Reject frames that are not a supported table shape.

        Returns
        -------
        ForecastRequest
            ``self`` after ``past``, ``future``, and ``static`` pass
            ``_check_frame``.

        Raises
        ------
        ValueError
            If a provided frame is not ``None`` and not a supported shape.
        """
        _check_frame(self.past, name="past")
        _check_frame(self.future, name="future")
        _check_frame(self.static, name="static")
        return self


class ForecastResponse(BaseModel):
    """User-facing forecast output with native-typed tables.

    JSON ``POST /forecast`` returns predictions as a column dict
    (``DataFrame.to_dict(as_series=False)``). ``Client.forecast`` restores
    pandas/polars/dict to match the caller's ``past`` type.

    ``request_id`` is assigned by the server routes, not by executors.

    Attributes
    ----------
    predictions : any, optional
        Point-forecast table including the time column. Shape-checked
        like request frames; may be ``None`` only if omitted (the JSON
        path always sets it from the executor).
    model : str
        Model id that produced the forecast (same id as the request).
    request_id : str
        Server-assigned UUID for this call. Used in HTTP 400 bodies when
        forecast routes fail.
    quantiles : any, optional
        Optional quantile table. Column names are executor-specific.

    Raises
    ------
    ValidationError
        If ``predictions`` or ``quantiles`` is not a supported table
        shape (or ``None``), or if other field types fail. Inner
        validators raise ``ValueError``, which Pydantic wraps.

    See Also
    --------
    CoercedForecastResponse
        Internal narwhals form produced by executors.
    fomo.client.client.Client.forecast
        Restores native frame types from the bytes path.
    """

    model_config = ConfigDict(json_schema_extra={"example": FORECAST_RESULT})

    predictions: Any = None
    model: str
    request_id: str
    quantiles: Any = None

    @model_validator(mode="after")
    def _check_frames(self) -> Self:
        """Reject prediction tables that are not a supported shape.

        Returns
        -------
        ForecastResponse
            ``self`` after shape checks.

        Raises
        ------
        ValueError
            If ``predictions`` or ``quantiles`` is an unsupported type.
        """
        _check_frame(self.predictions, name="predictions")
        _check_frame(self.quantiles, name="quantiles")
        return self


class CoercedForecastRequest(BaseModel):
    """Internal forecast input: narwhals frames plus column contracts.

    Executors, the scheduler, and the bytes decode path operate on this
    model. User code should build ``ForecastRequest`` and call
    ``coerce_request`` rather than constructing this directly, except in
    tests.

    Column rules (after narwhals conversion):

    * ``past`` must contain ``time`` and every ``target`` column.
    * If ``future`` is set, it must contain ``time``.

    Attributes
    ----------
    past : narwhals.DataFrame
        Past observations as a narwhals frame.
    time : str
        Time-index column name.
    target : list of str
        Target column names (``min_length=1``).
    fh : int
        Forecast steps (``> 0``).
    model : str, default ``"naive"``
        Loaded model id used by ``Scheduler.run`` to pick an executor.
    future : narwhals.DataFrame or None
        Future known covariates, or ``None``.
    static : narwhals.DataFrame or None
        Static features, or ``None``.
    quantiles : list of float or None
        Alphas forwarded to executors that support quantile forecasts.

    Raises
    ------
    ValidationError
        If required columns are missing or field types fail (including
        non-narwhals ``past``). Inner validators raise
        ``ValueError``, which Pydantic wraps. Messages list missing vs
        available columns.

    See Also
    --------
    ForecastRequest
        User-facing dual of this model.
    fomo.runtime.executors.sktime.converters.from_request
        Maps this model onto sktime ``y``, ``X``, ``fh`` (sktime only).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    past: nw.DataFrame[Any]
    time: str
    target: list[str] = Field(min_length=1)
    fh: int = Field(gt=0)
    model: str = "naive"
    future: nw.DataFrame[Any] | None = None
    static: nw.DataFrame[Any] | None = None
    quantiles: list[float] | None = None

    @model_validator(mode="after")
    def _check_frame_columns(self) -> Self:
        """Require time and target columns.

        Returns
        -------
        CoercedForecastRequest
            ``self`` after column checks.

        Raises
        ------
        ValueError
            If ``past`` (or ``future`` when present) is missing
            required columns.
        """
        _require_columns(self.past, [self.time, *self.target], frame_name="past")

        if self.future is not None:
            _require_columns(self.future, [self.time], frame_name="future")

        return self


class CoercedForecastResponse(BaseModel):
    """Internal forecast output: narwhals prediction tables.

    Executors return this. JSON ``POST /forecast`` converts tables with
    ``to_dict(as_series=False)``. The bytes path encodes them as Arrow
    IPC inside a ``FOMO`` envelope.

    ``request_id`` may be ``""`` from the sktime converter; server
    routes overwrite it with a UUID on the bytes path, and the JSON path
    builds a new ``ForecastResponse`` with a fresh id.

    Attributes
    ----------
    predictions : narwhals.DataFrame
        Point forecasts including the time column. Must have at least
        one column.
    model : str
        Model id that produced the forecast.
    request_id : str
        Call id; may be empty until the server fills it.
    quantiles : narwhals.DataFrame or None
        Optional quantile table; if present it must have at least one
        column.

    Raises
    ------
    ValidationError
        If ``predictions`` has no columns, ``quantiles`` is not
        ``None`` and has no columns, or field types fail. Inner
        validators raise ``ValueError``, which Pydantic wraps.

    See Also
    --------
    ForecastResponse
        User-facing dual of this model.
    fomo.types.converters.encode_response
        Splits metadata vs Arrow blobs for the bytes path.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    predictions: nw.DataFrame[Any]
    model: str
    request_id: str
    quantiles: nw.DataFrame[Any] | None = None

    @model_validator(mode="after")
    def _check_frame_columns(self) -> Self:
        """Reject empty prediction or quantile tables.

        Returns
        -------
        CoercedForecastResponse
            ``self`` after column checks.

        Raises
        ------
        ValueError
            If ``predictions`` (or a provided ``quantiles`` table) has
            no columns.
        """
        if not self.predictions.columns:
            raise ValueError("predictions table has no columns")
        if self.quantiles is not None and not self.quantiles.columns:
            raise ValueError("quantiles table has no columns")
        return self


class HealthError(BaseModel):
    """Structured error nested under ``HealthResult.error``.

    This is a response body, not a raised exception. The current
    ``GET /health`` handler always returns ``status="ok"`` with
    ``error`` omitted.

    Attributes
    ----------
    code : str
        Machine-readable error code (example: ``MODEL_NOT_LOADED``).
    message : str
        Human-readable explanation.
    """

    code: str
    message: str


class HealthResult(BaseModel):
    """Payload for ``GET /health``.

    Attributes
    ----------
    status : str
        Process status string. The live route currently returns ``"ok"``.
    error : HealthError or None
        Optional nested error. Omitted from JSON when ``None``.
    """

    model_config = ConfigDict(json_schema_extra={"example": HEALTH_OK})

    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    """Listing row for one **loaded** model.

    ``GET /models`` returns only models that ``bootstrap`` actually
    loaded. Registry catalog ids that were never passed to
    ``--load-models`` / ``load_models`` do not appear here.

    ``id`` is the model id used in forecast requests. ``executor`` is
    the plugin name (``sktime``, ``pytorch-forecasting``, ``custom``),
    not the model id.

    Attributes
    ----------
    id : str
        Loaded model id (registry key, zip stem, or caller-supplied id).
    executor : {"sktime", "pytorch-forecasting", "custom"}
        Executor plugin that loaded the artifact.
    source : {"object", "registry", "directory"}
        How ``resolve_model`` obtained the artifact: in-process
        forecaster, ``SKTIME_REGISTRY`` id, or a ``.zip`` path.
    """

    id: str
    executor: Literal["sktime", "pytorch-forecasting", "custom"]
    source: Literal["object", "registry", "directory"]


class ModelsResult(BaseModel):
    """Payload for ``GET /models``.

    Attributes
    ----------
    models : list of ModelInfo
        Currently loaded models. Empty if the process started with no
        ``load_models``.
    """

    model_config = ConfigDict(json_schema_extra={"example": MODELS_RESULT})

    models: list[ModelInfo]


class MemoryStats(BaseModel):
    """Process memory snapshot nested under ``StatsResult.memory``.

    Attributes
    ----------
    cpu_rss_mb : float or None
        Resident set size in MiB, or ``None`` if probing failed.
    gpu_mb : float or None
        CUDA memory allocated across devices in MiB, or ``None`` if
        torch/CUDA is unavailable.
    """

    cpu_rss_mb: float | None = None
    gpu_mb: float | None = None


class LatencySummary(BaseModel):
    """Per-model predict latency nested under ``ModelStats.latency_s``.

    Attributes
    ----------
    count : int
        Number of ``Scheduler.run`` calls recorded for this model.
    total : float
        Sum of wall times in seconds.
    mean : float or None
        ``total / count``, or ``None`` when ``count`` is 0.
    fastest : float or None
        Minimum recorded duration, or ``None`` when ``count`` is 0.
    slowest : float or None
        Maximum recorded duration, or ``None`` when ``count`` is 0.
    """

    count: int
    total: float
    mean: float | None = None
    fastest: float | None = None
    slowest: float | None = None


class RequestCounts(BaseModel):
    """Per-model request counters nested under ``ModelStats.requests``.

    Attributes
    ----------
    total : int
        ``ok + failed``.
    ok : int
        Predict calls that returned without raising.
    failed : int
        Predict calls that raised (still counted in latency).
    """

    total: int
    ok: int
    failed: int


class ModelStats(BaseModel):
    """Per-model load, warmup, and traffic nested under ``StatsResult.models``.

    Keys of ``StatsResult.models`` are model ids, not executor names.

    Attributes
    ----------
    executor : str or None
        Executor plugin name recorded at load time.
    load_s : float or None
        Wall time of ``Executor.load``.
    warmup_s : float or None
        Wall time of ``Executor.warmup``.
    requests : RequestCounts
        Success/failure counts from ``Scheduler.run``.
    latency_s : LatencySummary
        Predict-call wall times, including failed calls.
    """

    executor: str | None = None
    load_s: float | None = None
    warmup_s: float | None = None
    requests: RequestCounts
    latency_s: LatencySummary


class StatsResult(BaseModel):
    """Payload for ``GET /stats``.

    Built from ``fomo.logging.stats.Stats.snapshot`` via
    ``model_validate``.

    Attributes
    ----------
    uptime_s : float
        Seconds since the ``Stats`` instance was created (process
        bootstrap).
    memory : MemoryStats
        Best-effort RSS and GPU probes; fields may be ``None``.
    models : dict of str to ModelStats
        Per **loaded model id** metrics.
    """

    model_config = ConfigDict(json_schema_extra={"example": STATS_RESULT})

    uptime_s: float
    memory: MemoryStats
    models: dict[str, ModelStats]
