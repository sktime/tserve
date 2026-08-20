from typing import Any

import narwhals as nw
from sktime.forecasting.base import ForecastingHorizon

from fomo.runtime.executors.plugins import register
from fomo.runtime.executors.sktime.convertors import (
    as_prediction_frame,
    exog_columns,
    flatten_quantiles,
    request_frames,
    to_pandas,
)
from fomo.runtime.executors.sktime.registry import load_forecaster
from fomo.runtime.executors.sktime.utils import apply_model_config, warmup_forecaster
from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


@register("sktime")
class SktimeExecutor:
    def __init__(self) -> None:
        self._info: ModelInfo | None = None
        self._forecaster: Any = None

    def load(self, info: ModelInfo) -> None:
        if info.source != "registry":
            raise NotImplementedError(
                f"sktime executor cannot load source {info.source!r} yet (model {info.alias!r})"
            )
        self._info = info
        self._forecaster = load_forecaster(info.alias)
        warmup_forecaster(self._forecaster)

    def predict(self, request: ForecastRequest) -> ForecastResponse:
        apply_model_config(self._forecaster, request)
        y_frame, x_frame, x_future_frame = request_frames(request)
        series_id = tuple(request.series_id or ())
        target = tuple(request.target)

        fh = ForecastingHorizon(list(range(1, request.horizon + 1)), is_relative=True)
        y = to_pandas(
            y_frame,
            value_columns=target,
            time=request.time,
            series_id=series_id,
        )

        fit_kwargs: dict[str, Any] = {"y": y, "fh": fh}
        if x_frame is not None:
            fit_kwargs["X"] = to_pandas(
                x_frame,
                value_columns=exog_columns(x_frame, request),
                time=request.time,
                series_id=series_id,
            )
        self._forecaster.fit(**fit_kwargs)

        predict_kwargs: dict[str, Any] = {"fh": fh}
        if x_future_frame is not None:
            predict_kwargs["X"] = to_pandas(
                x_future_frame,
                value_columns=exog_columns(x_future_frame, request),
                time=request.time,
                series_id=series_id,
            )

        y_pred = self._forecaster.predict(**predict_kwargs)
        predictions = as_prediction_frame(y_pred, request)
        quantiles = None
        if request.quantiles:
            q_pred = self._forecaster.predict_quantiles(
                alpha=list(request.quantiles),
                **predict_kwargs,
            )
            quantiles = nw.from_native(flatten_quantiles(q_pred), eager_only=True)

        return ForecastResponse(
            predictions=predictions,
            quantiles=quantiles,
            model=request.model,
            request_id="",
        )
