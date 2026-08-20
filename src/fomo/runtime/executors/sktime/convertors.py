from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon

from fomo.types import ForecastRequest, ForecastResponse
from fomo.types.converters import table_to_frame


def from_request(request: ForecastRequest) -> tuple[
    pd.DataFrame,
    pd.DataFrame | None,
    pd.DataFrame | None,
    ForecastingHorizon,
    list[float] | None,
]:
    """Map a request onto the ``y``, ``X``, future ``X``, ``fh`` and quantiles sktime expects."""
    if request.series_id:
        raise ValueError("panel data (series_id) is not supported yet")

    history = _indexed(request.history, request)
    y = history[_columns(history, request.target, "history")]
    fh = ForecastingHorizon(range(1, request.horizon + 1), is_relative=True)
    quantiles = list(request.quantiles) if request.quantiles else None

    known = list(request.known_future or [])
    static = _static_values(request)
    if not known and not static:
        return y, None, None, fh, quantiles

    x = history[_columns(history, known, "history")].copy()
    x_future = _future_exog(request, known, history.index)
    for name, value in static.items():
        x[name] = value
        x_future[name] = value
    return y, x, x_future, fh, quantiles


def to_response(
    preds: pd.DataFrame,
    request: ForecastRequest,
    quantiles: pd.DataFrame | None = None,
) -> ForecastResponse:
    """Turn sktime predictions back into the tables the transport layer serializes."""
    return ForecastResponse(
        predictions=_as_table(preds, request),
        quantiles=None if quantiles is None else _as_table(_flatten(quantiles), request),
        model=request.model,
        request_id="",
    )


def _as_table(frame: pd.DataFrame, request: ForecastRequest) -> nw.DataFrame:
    frame = frame.copy()
    frame.index = frame.index.rename(request.time)
    return nw.from_native(frame.reset_index(), eager_only=True)


def _flatten(quantiles: pd.DataFrame) -> pd.DataFrame:
    """Collapse sktime's ``(variable, alpha)`` column index into flat ``var_alpha`` names."""
    if not isinstance(quantiles.columns, pd.MultiIndex):
        return quantiles
    quantiles = quantiles.copy()
    quantiles.columns = [
        f"{var}_{alpha}" if alpha != "" else str(var) for var, alpha in quantiles.columns
    ]
    return quantiles


def _indexed(table: Any, request: ForecastRequest) -> pd.DataFrame:
    frame = table_to_frame(table).to_pandas()
    if request.time not in frame.columns:
        raise ValueError(f"time column {request.time!r} is missing from the request tables")
    frame = frame.sort_values(request.time)
    index = pd.DatetimeIndex(pd.to_datetime(frame[request.time]), name=request.time)
    if request.freq is not None:
        index = _with_freq(index, request.freq)
    return frame.drop(columns=[request.time]).set_index(index)


def _with_freq(index: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    try:
        return pd.DatetimeIndex(index, freq=freq, name=index.name)
    except ValueError as exc:
        raise ValueError(f"timestamps do not match freq {freq!r}") from exc


def _columns(frame: pd.DataFrame, columns: list[str], origin: str) -> list[str]:
    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise ValueError(f"columns {missing} are missing from {origin}")
    return columns


def _static_values(request: ForecastRequest) -> dict[str, Any]:
    if request.static is None:
        return {}
    static = table_to_frame(request.static).to_pandas()
    if len(static) != 1:
        raise ValueError("static must hold exactly one row when series_id is not set")
    return static.iloc[0].to_dict()


def _future_exog(
    request: ForecastRequest,
    known: list[str],
    history_index: pd.DatetimeIndex,
) -> pd.DataFrame:
    if request.future is None:
        if known:
            raise ValueError("future is required when known_future is set")
        return pd.DataFrame(index=_future_index(request, history_index))
    future = _indexed(request.future, request)
    return future[_columns(future, known, "future")].copy()


def _future_index(request: ForecastRequest, history_index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    freq = request.freq or history_index.freq or pd.infer_freq(history_index)
    if freq is None:
        raise ValueError("freq is required when it cannot be inferred from history")
    return pd.date_range(
        history_index[-1],
        periods=request.horizon + 1,
        freq=freq,
        name=history_index.name,
    )[1:]
