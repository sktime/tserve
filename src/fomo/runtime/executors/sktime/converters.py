"""sktime converters: coerced request ↔ ``(y, X, X_future, fh)``.

This module is the domain layer used only inside ``SktimeExecutor``.
It does not move frames across the wire — that is
``fomo.types.converters``: native frames ↔ narwhals
↔ Arrow IPC ↔ FOMO envelope.

Executors only see ``CoercedForecastRequest`` /
``CoercedForecastResponse``. Field semantics live on those models.

Notes
-----
Time is the original ``time`` column, set as the pandas index. Indexes
already valid for sktime are left unchanged. JSON string timestamps are
converted with ``pandas.to_datetime``. ``to_response`` sets
``request_id=""``; server routes assign the real id (bytes path
overwrites after predict).

See Also
--------
fomo.types.models.CoercedForecastRequest
    Field semantics for the coerced payload.
fomo.types.converters
    Wire converters, not this module.
"""

from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.utils.validation.series import is_in_valid_index_types

from fomo.types import CoercedForecastRequest, CoercedForecastResponse


def from_request(
    request: CoercedForecastRequest,
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
    request : CoercedForecastRequest
        Internal forecast input. See
        ``fomo.types.models.CoercedForecastRequest`` for fields.

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
    fomo.types.models.CoercedForecastRequest
        Column contracts for the coerced payload.
    """
    past = _indexed(request.past, request)
    y: pd.DataFrame = past.loc[:, request.target]
    fh = ForecastingHorizon(range(1, request.fh + 1), is_relative=True)

    static = _static(request)
    if not static:
        return y, None, None, fh, request.quantiles

    if request.future is not None:
        future = _indexed(request.future, request)
    else:
        future = pd.DataFrame(index=fh.to_absolute(past.index[-1:]).to_pandas())

    x = pd.DataFrame(static, index=past.index)
    x_future = pd.DataFrame(static, index=future.index)
    return y, x, x_future, fh, request.quantiles


def to_response(
    preds: pd.DataFrame,
    request: CoercedForecastRequest,
    quantiles: pd.DataFrame | None = None,
) -> CoercedForecastResponse:
    """Turn sktime predictions into a ``CoercedForecastResponse``.

    Quantile columns are flattened to ``{var}_{alpha}`` before the
    time index is restored as a column. ``request_id`` is ``""``;
    server routes assign the call id (the bytes path overwrites after
    predict).

    Parameters
    ----------
    preds : pandas.DataFrame
        Point forecasts from ``predict``, time on the index.
    request : CoercedForecastRequest
        Supplies the time column name and ``model`` id.
    quantiles : pandas.DataFrame, optional
        Optional ``predict_quantiles`` result with a
        ``(variable, alpha)`` column index.

    Returns
    -------
    CoercedForecastResponse
        Narwhals ``predictions`` (and ``quantiles`` when provided),
        ``model=request.model``, ``request_id=""``.

    Raises
    ------
    ValidationError
        If ``predictions`` (or a provided quantile table) has no
        columns when constructing ``CoercedForecastResponse``.
    """
    predictions = _as_table(preds, request)
    quantile_table = (
        None if quantiles is None else _as_table(_flatten(quantiles), request)
    )

    return CoercedForecastResponse(
        predictions=predictions,
        quantiles=quantile_table,
        model=request.model,
        request_id="",
    )


def _indexed(table: nw.DataFrame[Any], request: CoercedForecastRequest) -> pd.DataFrame:
    """Set the time column as the index, converting JSON strings if needed.

    Indexes already valid for sktime (datetime, period, timedelta,
    range, integer) are unchanged. Anything else, typically a string
    timestamp column from JSON, is converted with ``pandas.to_datetime``.

    Parameters
    ----------
    table : narwhals.DataFrame
        Past or future table.
    request : CoercedForecastRequest
        Supplies the time column name.

    Returns
    -------
    pandas.DataFrame
        Frame indexed by ``request.time``.
    """
    frame = table.to_pandas().set_index(request.time)
    if not is_in_valid_index_types(frame.index):
        frame.index = pd.to_datetime(frame.index)
    return frame


def _static(request: CoercedForecastRequest) -> dict[str, Any]:
    """Read the first static row as values to broadcast over time.

    Parameters
    ----------
    request : CoercedForecastRequest
        Uses ``static`` when present.

    Returns
    -------
    dict of str to any
        Empty dict if ``static`` is ``None``; otherwise
        ``static.to_pandas().iloc[0].to_dict()``.
    """
    if request.static is None:
        return {}
    static: nw.DataFrame[Any] = request.static
    return static.to_pandas().iloc[0].to_dict()


def _as_table(
    frame: pd.DataFrame, request: CoercedForecastRequest
) -> nw.DataFrame[Any]:
    """Move the time index back into a column and wrap as narwhals.

    Parameters
    ----------
    frame : pandas.DataFrame
        Predictions (or flattened quantiles) with a time index.
    request : CoercedForecastRequest
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
