"""sktime **convertors**: coerced request ↔ ``(y, X, X_future, fh)``.

This module is the domain layer used only inside ``SktimeExecutor``.
It does not move frames across the wire — that is
``fomo.types.converters`` (note the spelling): native frames ↔ narwhals
↔ Arrow IPC ↔ FOMO envelope.

Executors only see ``CoercedForecastRequest`` /
``CoercedForecastResponse``. Field semantics live on those models.

Notes
-----
``context`` is unused. ``freq`` is accepted; indexes use
``freq="infer"``. ``params`` is not applied. ``series_id`` is
column-validated on ``CoercedForecastRequest``; ``from_request`` still
raises ``ValueError`` (panel not supported). ``to_response`` sets
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

from fomo.types import CoercedForecastRequest, CoercedForecastResponse


def from_request(request: CoercedForecastRequest) -> tuple[
    pd.DataFrame,
    pd.DataFrame | None,
    pd.DataFrame | None,
    ForecastingHorizon,
    list[float] | None,
]:
    """Map a coerced request onto sktime ``y``, ``X``, ``X_future``, ``fh``.

    Builds a relative ``ForecastingHorizon`` ``1 .. horizon``. Static
    features become constant columns via ``_static`` (first row of the
    static table). If there is no ``known_future`` and no static, both
    ``X`` and ``X_future`` are ``None``. If ``future`` is ``None`` while
    exogenous columns are still needed, the future index is
    ``fh.to_absolute(history.index[-1:]).to_pandas()``.

    Parameters
    ----------
    request : CoercedForecastRequest
        Internal forecast input. See
        ``fomo.types.models.CoercedForecastRequest`` for fields.

    Returns
    -------
    y : pandas.DataFrame
        Target columns from history, time column as ``DatetimeIndex``.
    X : pandas.DataFrame or None
        History exogenous (``known_future`` columns plus broadcast
        static), or ``None``.
    X_future : pandas.DataFrame or None
        Future exogenous with the same columns as ``X``, or ``None``.
    fh : sktime.forecasting.base.ForecastingHorizon
        Relative horizon ``range(1, horizon + 1)``.
    quantiles : list of float or None
        ``request.quantiles``, forwarded unchanged.

    Raises
    ------
    ValueError
        If ``request.series_id`` is set (panel data is not supported).

    See Also
    --------
    fomo.types.models.CoercedForecastRequest
        Column contracts and unused API fields (``context``, ``freq``,
        ``params``).
    """
    if request.series_id:
        raise ValueError(
            "panel data is not supported yet; omit series_id to forecast a single series"
        )

    history = _indexed(request.history, request)
    y: pd.DataFrame = history.loc[:, request.target]
    fh = ForecastingHorizon(range(1, request.horizon + 1), is_relative=True)

    known = request.known_future or []
    static = _static(request)
    if not known and not static:
        return y, None, None, fh, request.quantiles

    if request.future is not None:
        future = _indexed(request.future, request)
    else:
        future = pd.DataFrame(index=fh.to_absolute(history.index[-1:]).to_pandas())

    x: pd.DataFrame = history.loc[:, known].assign(**static)
    x_future: pd.DataFrame = future.loc[:, known].assign(**static)
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
    quantile_table = None if quantiles is None else _as_table(_flatten(quantiles), request)

    return CoercedForecastResponse(
        predictions=predictions,
        quantiles=quantile_table,
        model=request.model,
        request_id="",
    )


def _indexed(table: nw.DataFrame[Any], request: CoercedForecastRequest) -> pd.DataFrame:
    """Sort by time and set a ``DatetimeIndex`` with ``freq="infer"``.

    Drops the time column from the frame body and names the index
    ``request.time``. ``request.freq`` is not applied.

    Parameters
    ----------
    table : narwhals.DataFrame
        History or future table.
    request : CoercedForecastRequest
        Supplies the time column name.

    Returns
    -------
    pandas.DataFrame
        Time-sorted frame indexed by ``DatetimeIndex``.
    """
    frame = table.to_pandas().sort_values(request.time)
    index = pd.DatetimeIndex(
        pd.to_datetime(frame[request.time]), freq="infer", name=request.time
    )
    return frame.drop(columns=request.time).set_index(index)


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


def _as_table(frame: pd.DataFrame, request: CoercedForecastRequest) -> nw.DataFrame[Any]:
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
    return nw.from_native(frame.rename_axis(request.time).reset_index(), eager_only=True)


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
    return quantiles.set_axis([f"{var}_{alpha}" for var, alpha in quantiles.columns], axis=1)
