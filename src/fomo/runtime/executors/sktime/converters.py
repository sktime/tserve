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

    Builds a relative ``ForecastingHorizon`` ``1 .. fh``. Static
    features become constant columns via ``_static`` (first row of the
    static table). If there is no static, both ``X`` and ``X_future``
    are ``None``. If ``future`` is ``None`` while static columns are
    still needed, the future index is
    ``fh.to_absolute(past.index[-1:]).to_pandas()``.

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
        Past exogenous (broadcast static), or ``None``.
    X_future : pandas.DataFrame or None
        Future exogenous with the same columns as ``X``, or ``None``.
    fh : sktime.forecasting.base.ForecastingHorizon
        Relative horizon ``range(1, request.fh + 1)``.
    quantiles : list of float or None
        ``request.quantiles``, forwarded unchanged.

    See Also
    --------
    fomo.types.models.CoercedPredictRequest
        Column contracts for the coerced payload.
    """
    past = _indexed(request.past, request, name="past")
    y: pd.DataFrame = past.loc[:, request.target]
    fh = ForecastingHorizon(range(1, request.fh + 1), is_relative=True)

    static = _static(request)
    if not static:
        return y, None, None, fh, request.quantiles

    if request.future is not None:
        future = _indexed(request.future, request, name="future")
    else:
        future = pd.DataFrame(index=fh.to_absolute(past.index[-1:]).to_pandas())

    x = pd.DataFrame(static, index=past.index)
    x_future = pd.DataFrame(static, index=future.index)
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
