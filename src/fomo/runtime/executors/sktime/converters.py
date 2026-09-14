"""sktime converters: coerced request ↔ ``(y, X, X_future, fh)``.

This module is the domain layer used only inside ``SktimeExecutor``.
It does not move frames across the wire — that is
``fomo.types.converters``: native frames ↔ narwhals
↔ Arrow IPC ↔ FOMO envelope.

Executors only see ``CoercedPredictRequest`` /
``CoercedPredictResponse``. Field semantics live on those models.

Notes
-----
Time is the original ``time`` column, set as the pandas index. Indexes
already valid for sktime are left unchanged. JSON string timestamps are
converted with ``pandas.to_datetime``. ``to_response`` sets
``request_id=""``; server routes assign the real id (bytes path
overwrites after predict).

See Also
--------
fomo.types.models.CoercedPredictRequest
    Field semantics for the coerced payload.
fomo.types.converters
    Wire converters, not this module.
"""

from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.utils.validation.series import is_in_valid_index_types

from fomo.types import CoercedPredictRequest, CoercedPredictResponse


def from_request(
    request: CoercedPredictRequest,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame | None,
    pd.DataFrame | None,
    ForecastingHorizon,
    list[float] | None,
]:
    """Map a coerced request onto sktime ``y``, ``X``, ``X_future``, ``fh``.

    Builds a relative ``ForecastingHorizon`` ``1 .. fh``, carrying the
    frequency of the ``past`` time index so the horizon can place
    absolute timestamps.

    Exogenous features come from two places, and both land in ``X`` and
    ``X_future``:

    * time-varying covariates, the non-target columns present in both
      ``past`` and ``future``;
    * static features, constant columns from the first ``static`` row.

    Both are assembled by ``_exogenous``.

    With neither, ``X`` and ``X_future`` are both ``None``. ``X`` is
    indexed like ``past``; ``X_future`` is indexed by the forecast
    horizon, so a ``future`` holding extra rows is trimmed to it. When
    ``future`` is omitted the horizon index is generated, so static
    features alone need no ``future`` table.

    Parameters
    ----------
    request : CoercedPredictRequest
        Internal forecast input. See
        ``fomo.types.models.CoercedPredictRequest`` for fields.

    Returns
    -------
    y : pandas.DataFrame
        Target columns from past observations, indexed by ``time``.
        String timestamps (JSON) become ``DatetimeIndex``; integer and
        datetime indexes are passed through.
    X : pandas.DataFrame or None
        Past exogenous (covariates and broadcast static) indexed like
        ``past``, or ``None``.
    X_future : pandas.DataFrame or None
        Same columns as ``X`` over the forecast horizon, or ``None``.
    fh : sktime.forecasting.base.ForecastingHorizon
        Relative horizon ``range(1, request.fh + 1)``, with ``freq``
        set from the ``past`` time index.
    quantiles : list of float or None
        ``request.quantiles``, forwarded unchanged.

    Raises
    ------
    ValueError
        If a time column is unusable (``_indexed``), a datetime index
        has no inferable spacing (``_horizon``), ``static`` is present
        but empty (``_static``), or ``future`` does not cover the
        forecast horizon (``_exogenous``).

    See Also
    --------
    fomo.types.models.CoercedPredictRequest
        Column contracts for the coerced payload.
    """
    past = _indexed(request.past, request, name="past")

    y: pd.DataFrame = past.loc[:, request.target]
    fh = _horizon(past, request)
    x, x_future = _exogenous(past, request, fh)

    return y, x, x_future, fh, request.quantiles


def to_response(
    preds: pd.DataFrame,
    request: CoercedPredictRequest,
    quantiles: pd.DataFrame | None = None,
) -> CoercedPredictResponse:
    """Turn sktime predictions into a ``CoercedPredictResponse``.

    Quantile columns are flattened to ``{var}_{alpha}`` before the
    time index is restored as a column. ``request_id`` is ``""``;
    server routes assign the call id (the bytes path overwrites after
    predict).

    Parameters
    ----------
    preds : pandas.DataFrame
        Point forecasts from ``predict``, time on the index.
    request : CoercedPredictRequest
        Supplies the time column name and ``model`` id.
    quantiles : pandas.DataFrame, optional
        Optional ``predict_quantiles`` result with a
        ``(variable, alpha)`` column index.

    Returns
    -------
    CoercedPredictResponse
        Narwhals ``predictions`` (and ``quantiles`` when provided),
        ``model=request.model``, ``request_id=""``.

    Raises
    ------
    ValidationError
        If ``predictions`` (or a provided quantile table) has no
        columns when constructing ``CoercedPredictResponse``.
    """
    predictions = _as_table(preds, request)
    quantile_table = (
        None if quantiles is None else _as_table(_flatten(quantiles), request)
    )

    return CoercedPredictResponse(
        predictions=predictions,
        quantiles=quantile_table,
        model=request.model,
        request_id="",
    )


def _indexed(
    table: nw.DataFrame[Any], request: CoercedPredictRequest, *, name: str
) -> pd.DataFrame:
    """Set the time column as the index, converting JSON strings if needed.

    Indexes already valid for sktime (datetime, period, timedelta,
    range, integer) are unchanged. Anything else, typically a string
    timestamp column from JSON, is converted with ``pandas.to_datetime``.

    The resulting index is checked so sktime sees a usable time axis:
    no missing timestamps, sorted ascending, and no duplicates.

    Parameters
    ----------
    table : narwhals.DataFrame
        Past or future table.
    request : CoercedPredictRequest
        Supplies the time column name.
    name : str
        Frame name (``past`` or ``future``) used in error messages.

    Returns
    -------
    pandas.DataFrame
        Frame indexed by ``request.time``.

    Raises
    ------
    ValueError
        If the time column cannot be read as timestamps, or holds
        missing, unsorted, or duplicate values. sktime reports these
        as a long list of rejected input formats, so they are caught
        here instead.
    """
    time = request.time
    frame = table.to_pandas().set_index(time)

    if not is_in_valid_index_types(frame.index):
        try:
            frame.index = pd.to_datetime(frame.index)

        except (ValueError, TypeError) as error:
            raise ValueError(
                f"{name} column {time!r} could not be read as timestamps.\n\n"
                f"Original error: {error}\n\nUse one consistent format across "
                'every row, ideally ISO 8601 (e.g. "2024-01-01" or '
                f'"2024-01-01T00:00:00"), or send {time!r} as integers to '
                "index the series by position instead."
            ) from error

    index = frame.index

    if index.hasnans:
        raise ValueError(
            f"{name} column {time!r} has {int(index.isna().sum())} missing "
            f"timestamp(s) out of {len(index)}.\n\nEmpty strings and nulls "
            "become NaT, which sktime cannot place on a time axis. Give every "
            "row a timestamp, or drop the incomplete rows before sending."
        )

    if not index.is_monotonic_increasing:
        raise ValueError(
            f"{name} column {time!r} is not sorted in increasing order.\n\n"
            "sktime needs observations oldest first. Sort the rows by "
            f"{time!r} before sending, e.g. pandas "
            f"`df.sort_values({time!r})`."
        )

    if not index.is_unique:
        duplicates = index[index.duplicated()].unique()
        raise ValueError(
            f"{name} column {time!r} has {len(duplicates)} duplicate "
            f"timestamp(s), e.g. {list(duplicates[:3])}.\n\nEach row must be "
            "one point in time. Aggregate the repeated rows (sum, mean, …) or "
            "drop them so every timestamp appears once."
        )

    return frame


def _horizon(past: pd.DataFrame, request: CoercedPredictRequest) -> ForecastingHorizon:
    """Build the relative forecasting horizon ``1 .. request.fh``.

    ``ForecastingHorizon.to_absolute`` turns those relative steps into
    timestamps by multiplying them by the index frequency, so the
    horizon is given the spacing of the ``past`` index. It has to be
    read here, from the full index: the cutoff sktime derives from it,
    ``past.index[-1:]``, is one element long and carries no spacing of
    its own.

    Parameters
    ----------
    past : pandas.DataFrame
        Indexed past frame, from ``_indexed``.
    request : CoercedPredictRequest
        Supplies ``fh`` and the time column name for error messages.

    Returns
    -------
    sktime.forecasting.base.ForecastingHorizon
        Relative horizon, with ``freq`` set for a ``DatetimeIndex`` and
        ``None`` for integer, range, and period indexes, which are
        positional and need no frequency.

    Raises
    ------
    ValueError
        If a ``DatetimeIndex`` has no regular spacing to infer.
    """
    index = past.index
    freq = None

    if isinstance(index, pd.DatetimeIndex):
        freq = index.freqstr or index.inferred_freq

        if freq is None:
            raise ValueError(
                f"could not infer how far apart the {request.time!r} timestamps "
                f"are, from {len(index)} row(s).\n\nForecasting future "
                "timestamps needs a regular spacing. Send at least 3 rows at a "
                "fixed interval (hourly, daily, monthly, …) with no gaps, or "
                f"index the series by position using integers in "
                f"{request.time!r}."
            )

    return ForecastingHorizon(range(1, request.fh + 1), is_relative=True, freq=freq)


def _exogenous(
    past: pd.DataFrame, request: CoercedPredictRequest, fh: ForecastingHorizon
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Build ``X`` and ``X_future`` from covariates and static values.

    A non-target column becomes a time-varying covariate when it
    appears in **both** ``past`` and ``future``: sktime needs its
    history to fit and its future values to predict. A column on only
    one side is left out, having no future values or no history. This
    is the same split ``coerce_request`` applies when inferring
    ``target``, which excludes columns present in ``future``.

    Static values are added as constant columns. Both tables are built
    from the same column list so they agree across ``fit`` and
    ``predict``, as sktime requires.

    Parameters
    ----------
    past : pandas.DataFrame
        Indexed past frame, from ``_indexed``.
    request : CoercedPredictRequest
        Supplies ``future``, ``static``, and ``target``.
    fh : sktime.forecasting.base.ForecastingHorizon
        Horizon whose absolute timestamps ``X_future`` must cover.

    Returns
    -------
    X : pandas.DataFrame or None
        Exogenous features over the ``past`` index, or ``None`` when
        there are no covariates and no static values.
    X_future : pandas.DataFrame or None
        Same columns over the forecast horizon, or ``None``.

    Raises
    ------
    ValueError
        If ``future`` is present but misses a timestamp being forecast.
    """
    # 1. Decide which columns can carry exogenous information

    future = (
        _indexed(request.future, request, name="future")
        if request.future is not None
        else None
    )
    static = _static(request)
    exog = (
        []
        if future is None
        else [
            column
            for column in past.columns
            if column not in request.target and column in future.columns
        ]
    )

    if not exog and not static:
        return None, None

    # 2. Line the future frame up with the timestamps being forecast

    horizon = fh.to_absolute(past.index[-1:]).to_pandas()

    if future is None:
        future = pd.DataFrame(index=horizon)

    else:
        missing = horizon.difference(future.index)

        if not missing.empty:
            raise ValueError(
                f"future is missing {len(missing)} of the {len(horizon)} "
                f"timestamp(s) being forecast, e.g. {list(missing[:3])}.\n\n"
                f"fh={request.fh} forecasts the next {request.fh} step(s) after "
                f"the last past row, so future must hold a row for each of "
                f"{list(horizon[:3])}... Send future rows that continue past, "
                "or omit future to have them generated."
            )

        future = future.reindex(horizon)

    # 3. Build both tables from the same columns, in the same order

    x = past.loc[:, exog].copy()
    x_future = future.loc[:, exog].copy()

    for column, value in static.items():
        x[column] = value
        x_future[column] = value

    return x, x_future


def _static(request: CoercedPredictRequest) -> dict[str, Any]:
    """Read the first static row as values to broadcast over time.

    Parameters
    ----------
    request : CoercedPredictRequest
        Uses ``static`` when present.

    Returns
    -------
    dict of str to any
        Empty dict if ``static`` is ``None``; otherwise
        ``static.to_pandas().iloc[0].to_dict()``.

    Raises
    ------
    ValueError
        If ``static`` is present but has no rows to read.
    """
    if request.static is None:
        return {}

    static: nw.DataFrame[Any] = request.static
    frame = static.to_pandas()

    if frame.empty:
        raise ValueError(
            f"static has columns {list(frame.columns)} but no rows.\n\nStatic "
            "features are read from a single row and held constant over time, "
            'so give each column exactly one value, e.g. {"store": ["urban"]}, '
            "or omit static entirely."
        )

    return frame.iloc[0].to_dict()


def _as_table(frame: pd.DataFrame, request: CoercedPredictRequest) -> nw.DataFrame[Any]:
    """Move the time index back into a column and wrap as narwhals.

    Parameters
    ----------
    frame : pandas.DataFrame
        Predictions (or flattened quantiles) with a time index.
    request : CoercedPredictRequest
        ``time`` becomes the name of the restored index column.

    Returns
    -------
    narwhals.DataFrame
        Eager frame from ``rename_axis(time).reset_index()``.
    """
    return nw.from_native(
        frame.rename_axis(request.time).reset_index(), eager_only=True
    )


def _flatten(quantiles: pd.DataFrame) -> pd.DataFrame:
    """Collapse a ``(variable, alpha)`` column index into ``var_alpha`` names.

    Parameters
    ----------
    quantiles : pandas.DataFrame
        sktime ``predict_quantiles`` table.

    Returns
    -------
    pandas.DataFrame
        Same values with flattened columns ``f"{var}_{alpha}"``.
    """
    return quantiles.set_axis(
        [f"{var}_{alpha}" for var, alpha in quantiles.columns], axis=1
    )
