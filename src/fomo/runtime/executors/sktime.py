from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.registry import craft

from fomo.runtime.executors.plugins import register
from fomo.runtime.registry import SKTIME_REGISTRY
from fomo.types import ForecastRequest, ForecastResponse, ModelInfo
from fomo.types.converters import as_frame

_WARMUP_Y = pd.DataFrame({"y": [0.0, 1.0, 2.0]})
_WARMUP_FH = ForecastingHorizon([1], is_relative=True)


def _warmup_forecaster(forecaster: Any) -> None:
    forecaster.fit(_WARMUP_Y, fh=_WARMUP_FH)
    forecaster.predict()


def _index_columns(request: ForecastRequest) -> list[str]:
    return list(request.series_id or []) + [request.time]


def _select(frame: nw.DataFrame, columns: list[str]) -> nw.DataFrame:
    keep = [col for col in columns if col in frame.columns]
    return frame.select(keep)


def _join_static(
    frame: nw.DataFrame,
    static: nw.DataFrame,
    series_id: list[str],
) -> nw.DataFrame:
    return frame.join(static, on=series_id, how="left")


def _future_index_from_freq(request: ForecastRequest, hist: pd.DataFrame) -> pd.DataFrame:
    if request.freq is None:
        raise ValueError("freq is required when static is set without future")
    keys = list(request.series_id or [])
    rows: list[list[Any]] = []
    if keys:
        for key, group in hist.groupby(keys, sort=False):
            key_t = key if isinstance(key, tuple) else (key,)
            last = group[request.time].max()
            times = pd.date_range(last, periods=request.horizon + 1, freq=request.freq)[1:]
            for ts in times:
                rows.append([*key_t, ts])
    else:
        last = hist[request.time].max()
        times = pd.date_range(last, periods=request.horizon + 1, freq=request.freq)[1:]
        rows.extend([ts] for ts in times)
    return pd.DataFrame(rows, columns=keys + [request.time])


def _request_frames(
    request: ForecastRequest,
) -> tuple[nw.DataFrame, nw.DataFrame | None, nw.DataFrame | None]:
    hist = as_frame(request.history)
    index_cols = _index_columns(request)
    y = _select(hist, index_cols + list(request.target))

    known = list(request.known_future or [])
    if not known and request.static is None:
        return y, None, None

    x = _select(hist, index_cols + known)
    if request.future is not None:
        x_future = _select(as_frame(request.future), index_cols + known)
    else:
        x_future = nw.from_native(
            _future_index_from_freq(request, hist.to_pandas()),
            eager_only=True,
        )

    if request.static is not None:
        static = as_frame(request.static)
        series_id = list(request.series_id or [])
        x = _join_static(x, static, series_id)
        x_future = _join_static(x_future, static, series_id)

    return y, x, x_future


def _to_pandas(
    frame: nw.DataFrame,
    *,
    value_columns: tuple[str, ...],
    time: str,
    series_id: tuple[str, ...],
) -> pd.DataFrame:
    pdf = frame.to_pandas()
    index_cols = [col for col in (*series_id, time) if col in pdf.columns]
    if time in pdf.columns:
        pdf[time] = pd.to_datetime(pdf[time])
    if index_cols:
        pdf = pdf.set_index(index_cols)
    return pdf[list(value_columns)]


def _prediction_frame(
    y_pred: pd.Series | pd.DataFrame,
    *,
    target: tuple[str, ...],
    time: str,
    series_id: tuple[str, ...],
) -> pd.DataFrame:
    if isinstance(y_pred, pd.Series):
        y_pred = y_pred.to_frame(name=target[0])
    y_pred = y_pred.copy()
    expected = list(series_id) + [time]
    if isinstance(y_pred.index, pd.MultiIndex):
        names = [
            current if current is not None else expected[i]
            for i, current in enumerate(y_pred.index.names)
        ]
        y_pred.index = y_pred.index.set_names(names)
    elif y_pred.index.name is None:
        y_pred.index.name = time
    return y_pred.reset_index()


def _flatten_quantiles(qdf: pd.DataFrame) -> pd.DataFrame:
    if isinstance(qdf.columns, pd.MultiIndex):
        qdf = qdf.copy()
        qdf.columns = [
            f"{var}_{quantile}" if quantile != "" else str(var)
            for var, quantile in qdf.columns.to_list()
        ]
    return qdf.reset_index()


def _apply_model_config(forecaster: Any, request: ForecastRequest) -> None:
    freq = request.freq or (request.params or {}).get("freq")
    if freq is not None and hasattr(forecaster, "freq"):
        forecaster.freq = freq


def _exog_columns(frame: nw.DataFrame, request: ForecastRequest) -> tuple[str, ...]:
    skip = set(request.series_id or ()) | {request.time}
    return tuple(col for col in frame.columns if col not in skip)


def _as_prediction_frame(
    y_pred: pd.Series | pd.DataFrame,
    request: ForecastRequest,
) -> nw.DataFrame:
    return nw.from_native(
        _prediction_frame(
            y_pred,
            target=tuple(request.target),
            time=request.time,
            series_id=tuple(request.series_id or ()),
        ),
        eager_only=True,
    )


@register("sktime")
class SktimeExecutor:
    def __init__(self) -> None:
        self._info: ModelInfo | None = None
        self._forecaster: Any = None

    def load(self, info: ModelInfo, model: Any) -> None:
        self._info = info

        if info.source == "registry":
            self._forecaster = craft(SKTIME_REGISTRY[model]["spec"])
        elif info.source == "object":
            self._forecaster = model

        _warmup_forecaster(self._forecaster)

        raise NotImplementedError(
            f"sktime executor cannot load source {info.source!r} yet (model {info.alias!r})"
        )

    def predict(self, request: ForecastRequest) -> ForecastResponse:
        if self._info is None or self._forecaster is None:
            raise RuntimeError("sktime executor has no model loaded")
        if request.model != self._info.alias:
            raise RuntimeError(
                f"executor for {self._info.alias!r} cannot run {request.model!r}"
            )

        _apply_model_config(self._forecaster, request)
        y_frame, x_frame, x_future_frame = _request_frames(request)
        series_id = tuple(request.series_id or ())
        target = tuple(request.target)

        fh = ForecastingHorizon(list(range(1, request.horizon + 1)), is_relative=True)
        y = _to_pandas(
            y_frame,
            value_columns=target,
            time=request.time,
            series_id=series_id,
        )

        fit_kwargs: dict[str, Any] = {"y": y, "fh": fh}
        if x_frame is not None:
            fit_kwargs["X"] = _to_pandas(
                x_frame,
                value_columns=_exog_columns(x_frame, request),
                time=request.time,
                series_id=series_id,
            )
        self._forecaster.fit(**fit_kwargs)

        predict_kwargs: dict[str, Any] = {"fh": fh}
        if x_future_frame is not None:
            predict_kwargs["X"] = _to_pandas(
                x_future_frame,
                value_columns=_exog_columns(x_future_frame, request),
                time=request.time,
                series_id=series_id,
            )

        y_pred = self._forecaster.predict(**predict_kwargs)
        predictions = _as_prediction_frame(y_pred, request)
        quantiles = None
        if request.quantiles:
            q_pred = self._forecaster.predict_quantiles(
                alpha=list(request.quantiles),
                **predict_kwargs,
            )
            quantiles = nw.from_native(_flatten_quantiles(q_pred), eager_only=True)

        return ForecastResponse(
            predictions=predictions,
            quantiles=quantiles,
            model=request.model,
            request_id="",
        )
