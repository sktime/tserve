from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.registry import craft

from fomo.runtime.executors.plugins import register
from fomo.types import ModelInfo
from fomo.types.converters import validate_job
from fomo.types.models import ForecastJob, ForecastResult

_WARMUP_Y = pd.DataFrame({"y": [0.0, 1.0, 2.0]})
_WARMUP_FH = ForecastingHorizon([1], is_relative=True)


def _warmup_forecaster(forecaster: Any) -> None:
    forecaster.fit(_WARMUP_Y, fh=_WARMUP_FH)
    forecaster.predict()


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


def _apply_model_config(forecaster: Any, job: ForecastJob) -> None:
    freq = job.freq or job.params.get("freq")
    if freq is not None and hasattr(forecaster, "freq"):
        forecaster.freq = freq


@register("sktime")
class SktimeExecutor:
    def __init__(self) -> None:
        self._spec: ModelInfo | None = None
        self._forecaster: Any = None

    def load(self, spec: ModelInfo) -> None:
        self._spec = spec
        self._forecaster = craft(spec.spec)
        _warmup_forecaster(self._forecaster)

    def predict(self, job: ForecastJob) -> ForecastResult:
        validate_job(job)
        if self._spec is None or self._forecaster is None:
            raise RuntimeError("sktime executor has no model loaded")
        if job.model != self._spec.alias:
            raise RuntimeError(
                f"executor for {self._spec.alias!r} cannot run {job.model!r}"
            )

        _apply_model_config(self._forecaster, job)

        fh = ForecastingHorizon(list(range(1, job.horizon + 1)), is_relative=True)
        y = _to_pandas(
            job.y,
            value_columns=job.target,
            time=job.time,
            series_id=job.series_id,
        )

        x_past = None
        if job.X is not None:
            exog_cols = tuple(c for c in job.X.columns if c not in job.series_id and c != job.time)
            x_past = _to_pandas(
                job.X,
                value_columns=exog_cols,
                time=job.time,
                series_id=job.series_id,
            )

        fit_kwargs: dict[str, Any] = {"y": y, "fh": fh}
        if x_past is not None:
            fit_kwargs["X"] = x_past
        self._forecaster.fit(**fit_kwargs)

        predict_kwargs: dict[str, Any] = {"fh": fh}
        if job.X_future is not None:
            exog_cols = tuple(
                c for c in job.X_future.columns if c not in job.series_id and c != job.time
            )
            predict_kwargs["X"] = _to_pandas(
                job.X_future,
                value_columns=exog_cols,
                time=job.time,
                series_id=job.series_id,
            )

        if job.quantiles:
            q_pred = self._forecaster.predict_quantiles(
                alpha=list(job.quantiles),
                **predict_kwargs,
            )
            y_pred = self._forecaster.predict(**predict_kwargs)
            return ForecastResult(
                y_pred=nw.from_native(
                    _prediction_frame(
                        y_pred, target=job.target, time=job.time, series_id=job.series_id
                    ),
                    eager_only=True,
                ),
                quantiles=nw.from_native(_flatten_quantiles(q_pred), eager_only=True),
                model=job.model,
            )

        y_pred = self._forecaster.predict(**predict_kwargs)
        return ForecastResult(
            y_pred=nw.from_native(
                _prediction_frame(
                    y_pred, target=job.target, time=job.time, series_id=job.series_id
                ),
                eager_only=True,
            ),
            model=job.model,
        )
