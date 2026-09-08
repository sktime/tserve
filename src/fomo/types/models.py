"""Pydantic schemas for predict requests, responses, and server status.

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
    Turn ``PredictRequest`` into ``CoercedPredictRequest`` and pack
    frames as Arrow IPC for the bytes path.
fomo.types._checks
    Shape checks run when constructing user-facing predict models.
"""

from typing import Any, Literal, Self

import narwhals as nw
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fomo.types._checks import _check_frame, _require_columns
from fomo.types._examples import (
    HEALTH_OK,
    MODELS_RESULT,
    PREDICT_REQUEST,
    PREDICT_RESULT,
    STATS_RESULT,
)


class PredictRequest(BaseModel):
    """Predict input. Same fields on JSON ``POST /predict`` and ``Client.predict``.

    Tables may be a column dict (name → list), a row matrix
    ``{"columns": [...], "data": [[...], ...]}``, pandas, polars,
    pyarrow, or Narwhals.

    ``model`` is a **loaded** id (see ``GET /models``), not an executor
    name such as ``"sktime"``.

    Attributes
    ----------
    past : any
        Past observations. After coercion must include ``time`` and
        every ``target``.
    time : str or None, optional
        Time-index column. When omitted, the first column of ``past``.
    target : str or list of str or None, optional
        Target columns. A string becomes a one-element list. When
        omitted, remaining ``past`` columns (minus ``future`` columns).
    fh : int
        Prediction steps ahead (must be ``> 0``).
    model : str, default ``"naive"``
        Loaded model id.
    future : any, optional
        Future timestamps when using ``static``.
    static : any, optional
        One-row static features, broadcast over time.
    quantiles : list of float, optional
        Quantile alphas, e.g. ``[0.1, 0.5, 0.9]``.

    Notes
    -----
    ``past`` is a table, and ``time`` names one of its columns.

    See Also
    --------
    [Data specification](../client/data.md)
        Table formats, column roles, and inference rules.
    [HTTP predict route](../reference/http.md#post-predict)
        JSON request behavior and status codes.
    [Python client](../client/python.md)
        Arrow transport through ``Client.predict``.
    """

    model_config = ConfigDict(json_schema_extra={"example": PREDICT_REQUEST})

    past: Any
    time: str | None = None
    target: str | list[str] | None = None
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
        PredictRequest
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


class PredictResponse(BaseModel):
    """Predict output.

    JSON ``POST /predict`` returns tables as column dicts.
    ``Client.predict`` restores the type of the caller's ``past``.

    Attributes
    ----------
    predictions : any
        Point-forecast table, including the time column.
    model : str
        Model id that produced the forecast.
    request_id : str
        Server-assigned UUID for this call.
    quantiles : any, optional
        Quantile table when requested; column names are
        ``{variable}_{alpha}``.

    See Also
    --------
    [Data specification](../client/data.md#response)
        JSON and native-table response behavior.
    [HTTP predict route](../reference/http.md#post-predict)
        JSON response and failure statuses.
    [Python client](../client/python.md#send-a-prediction)
        Access the result returned by ``Client.predict``.
    """

    model_config = ConfigDict(json_schema_extra={"example": PREDICT_RESULT})

    predictions: Any = None
    model: str
    request_id: str
    quantiles: Any = None

    @model_validator(mode="after")
    def _check_frames(self) -> Self:
        """Reject prediction tables that are not a supported shape.

        Returns
        -------
        PredictResponse
            ``self`` after shape checks.

        Raises
        ------
        ValueError
            If ``predictions`` or ``quantiles`` is an unsupported type.
        """
        _check_frame(self.predictions, name="predictions")
        _check_frame(self.quantiles, name="quantiles")
        return self


class CoercedPredictRequest(BaseModel):
    """Internal predict input: narwhals frames plus column contracts.

    Executors, the scheduler, and the bytes decode path operate on this
    model. User code should build ``PredictRequest`` and call
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
        Time-index column name. Always resolved (never ``None``).
    target : list of str
        Target column names (``min_length=1``). Always a list.
    fh : int
        Prediction steps (``> 0``).
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
    PredictRequest
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
        CoercedPredictRequest
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


class CoercedPredictResponse(BaseModel):
    """Internal predict output: narwhals prediction tables.

    Executors return this. JSON ``POST /predict`` converts tables with
    ``to_dict(as_series=False)``. The bytes path encodes them as Arrow
    IPC inside a ``FOMO`` envelope.

    ``request_id`` may be ``""`` from the sktime converter; server
    routes overwrite it with a UUID on the bytes path, and the JSON path
    builds a new ``PredictResponse`` with a fresh id.

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
    PredictResponse
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
        CoercedPredictResponse
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

    See Also
    --------
    [Errors](../reference/errors.md)
        HTTP statuses and Python exceptions.
    [HTTP status routes](../reference/http.md#status-routes)
        Current health-route behavior.
    """

    code: str
    message: str


class HealthResult(BaseModel):
    """Payload for ``GET /health``.

    Attributes
    ----------
    status : str
        Currently always ``"ok"``.
    error : HealthError or None
        Unused on the live route.

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Health semantics and response shape.
    """

    model_config = ConfigDict(json_schema_extra={"example": HEALTH_OK})

    status: str
    error: HealthError | None = None


class ModelInfo(BaseModel):
    """One **loaded** model (a row of ``GET /models``).

    Attributes
    ----------
    id : str
        Id used in predict ``model``.
    executor : {"sktime", "pytorch-forecasting", "custom"}
        Plugin that loaded the artifact.
    source : {"object", "registry", "directory"}
        Registry id, saved ``.zip``, or in-process estimator.

    See Also
    --------
    [Models catalog](../models/index.md)
        Registry ids the server can load.
    [HTTP status routes](../reference/http.md#status-routes)
        Loaded-model listing and source values.
    """

    id: str
    executor: Literal["sktime", "pytorch-forecasting", "custom"]
    source: Literal["object", "registry", "directory"]


class ModelsResult(BaseModel):
    """Payload for ``GET /models``.

    Attributes
    ----------
    models : list of ModelInfo
        Currently loaded models. Empty if nothing was loaded.

    See Also
    --------
    [Models catalog](../models/index.md)
        Available registry ids; this result contains only loaded ids.
    [HTTP status routes](../reference/http.md#status-routes)
        ``GET /models`` response behavior.
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

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Full ``GET /stats`` response.
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

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Full ``GET /stats`` response.
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

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Full ``GET /stats`` response.
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

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Full ``GET /stats`` response.
    """

    executor: str | None = None
    load_s: float | None = None
    warmup_s: float | None = None
    requests: RequestCounts
    latency_s: LatencySummary


class StatsResult(BaseModel):
    """Payload for ``GET /stats``.

    Attributes
    ----------
    uptime_s : float
        Seconds since process start.
    memory : MemoryStats
        RSS and GPU probes; fields may be ``None``.
    models : dict of str to ModelStats
        Per **loaded model id** load, warmup, and latency.

    See Also
    --------
    [HTTP status routes](../reference/http.md#status-routes)
        Stats semantics and response example.
    """

    model_config = ConfigDict(json_schema_extra={"example": STATS_RESULT})

    uptime_s: float
    memory: MemoryStats
    models: dict[str, ModelStats]
