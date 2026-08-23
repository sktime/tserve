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
    """Map a request onto the ``y``, ``X``, future ``X``, ``fh`` and quantiles sktime expects."""
    if request.series_id:
        raise ValueError("panel data (series_id) is not supported yet")

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
    """Turn sktime predictions back into the tables the transport layer serializes."""
    predictions = _as_table(preds, request)
    quantile_table = None if quantiles is None else _as_table(_flatten(quantiles), request)

    return CoercedForecastResponse(
        predictions=predictions,
        quantiles=quantile_table,
        model=request.model,
        request_id="",
    )


def _indexed(table: nw.DataFrame[Any], request: CoercedForecastRequest) -> pd.DataFrame:
    frame = table.to_pandas().sort_values(request.time)
    index = pd.DatetimeIndex(
        pd.to_datetime(frame[request.time]), freq="infer", name=request.time
    )
    return frame.drop(columns=request.time).set_index(index)


def _static(request: CoercedForecastRequest) -> dict[str, Any]:
    """Read the single row of static features as values to broadcast over time."""
    if request.static is None:
        return {}
    static: nw.DataFrame[Any] = request.static
    return static.to_pandas().iloc[0].to_dict()


def _as_table(frame: pd.DataFrame, request: CoercedForecastRequest) -> nw.DataFrame[Any]:
    return nw.from_native(frame.rename_axis(request.time).reset_index(), eager_only=True)


def _flatten(quantiles: pd.DataFrame) -> pd.DataFrame:
    """Collapse sktime's ``(variable, alpha)`` column index into flat ``var_alpha`` names."""
    return quantiles.set_axis([f"{var}_{alpha}" for var, alpha in quantiles.columns], axis=1)
