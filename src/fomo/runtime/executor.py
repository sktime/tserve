from typing import Any

import narwhals as nw
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon
from sktime.registry import craft

from fomo.runtime.adapt import validate_job
from fomo.runtime.registry import get_model
from fomo.runtime.types import ForecastJob, ForecastResult

_WARMUP_Y = pd.DataFrame({"y": [0.0, 1.0, 2.0]})
_WARMUP_FH = ForecastingHorizon([1], is_relative=True)


def _warmup_forecaster(forecaster: Any) -> None:
    forecaster.fit(_WARMUP_Y, fh=_WARMUP_FH)
    forecaster.predict()


def _to_pandas(
    frame: nw.DataFrame,
    *,
    value_columns: tuple[str, ...],
    time_column: str | None,
    id_columns: tuple[str, ...],
) -> pd.DataFrame:
    pdf = frame.to_pandas()
    index_cols = [col for col in (*id_columns, time_column) if col and col in pdf.columns]
    if time_column and time_column in pdf.columns:
        pdf[time_column] = pd.to_datetime(pdf[time_column])
    if index_cols:
        pdf = pdf.set_index(index_cols)
    return pdf[list(value_columns)]


def _flatten_quantiles(qdf: pd.DataFrame) -> pd.DataFrame:
    if isinstance(qdf.columns, pd.MultiIndex):
        qdf = qdf.copy()
        qdf.columns = [
            f"{var}_{quantile}" if quantile != "" else str(var)
            for var, quantile in qdf.columns.to_list()
        ]
    return qdf.reset_index()


def _apply_model_config(forecaster: Any, job: ForecastJob) -> None:
    freq = job.freq or job.model_config.get("freq")
    if freq is not None and hasattr(forecaster, "freq"):
        forecaster.freq = freq


class Executor:
    def __init__(self) -> None:
        self._forecasters: dict[str, Any] = {}

    def load(self, model_ref: str) -> None:
        if model_ref in self._forecasters:
            return
        spec = get_model(model_ref)
        forecaster = craft(spec.spec)
        _warmup_forecaster(forecaster)
        self._forecasters[model_ref] = forecaster

    def predict(self, job: ForecastJob) -> ForecastResult:
        validate_job(job)
        forecaster = self._forecasters.get(job.model)
        if forecaster is None:
            raise RuntimeError(
                f"model {job.model!r} is not loaded; add it to FOMO_PRELOAD_MODELS or call load()"
            )

        _apply_model_config(forecaster, job)

        fh = ForecastingHorizon(list(range(1, job.horizon + 1)), is_relative=True)
        y = _to_pandas(
            job.y,
            value_columns=job.target_columns,
            time_column=job.time_column,
            id_columns=job.id_columns,
        )

        x_past = None
        if job.X is not None:
            exog_cols = tuple(c for c in job.X.columns if c not in job.id_columns and c != job.time_column)
            x_past = _to_pandas(
                job.X,
                value_columns=exog_cols,
                time_column=job.time_column,
                id_columns=job.id_columns,
            )

        fit_kwargs: dict[str, Any] = {"y": y, "fh": fh}
        if x_past is not None:
            fit_kwargs["X"] = x_past
        forecaster.fit(**fit_kwargs)

        predict_kwargs: dict[str, Any] = {"fh": fh}
        if job.X_future is not None:
            exog_cols = tuple(
                c for c in job.X_future.columns if c not in job.id_columns and c != job.time_column
            )
            predict_kwargs["X"] = _to_pandas(
                job.X_future,
                value_columns=exog_cols,
                time_column=job.time_column,
                id_columns=job.id_columns,
            )

        if job.quantiles:
            q_pred = forecaster.predict_quantiles(
                alpha=list(job.quantiles),
                **predict_kwargs,
            )
            y_pred = forecaster.predict(**predict_kwargs)
            return ForecastResult(
                y_pred=nw.from_native(y_pred),
                quantiles=nw.from_native(_flatten_quantiles(q_pred)),
                model=job.model,
            )

        y_pred = forecaster.predict(**predict_kwargs)
        return ForecastResult(y_pred=nw.from_native(y_pred), model=job.model)

    def health(self) -> dict:
        return {
            "status": "ok",
            "loaded_models": sorted(self._forecasters.keys()),
        }
