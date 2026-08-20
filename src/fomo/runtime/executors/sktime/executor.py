from typing import Any

from fomo.runtime.executors.plugins import register
from fomo.runtime.executors.sktime.convertors import from_request, to_response
from fomo.runtime.executors.sktime.registry import load_forecaster
from fomo.types import ForecastRequest, ForecastResponse, ModelInfo


@register("sktime")
class SktimeExecutor:
    def __init__(self) -> None:
        self._info: ModelInfo | None = None
        self._forecaster: Any = None

    def load(self, info: ModelInfo) -> None:
        self._info = info
        self._forecaster = load_forecaster(info.alias)

    def predict(self, request: ForecastRequest) -> ForecastResponse:
        y, X, X_future, fh, quantiles = from_request(request)

        self._forecaster.fit(y=y, X=X, fh=fh)
        pred = self._forecaster.predict(X=X_future, fh=fh)
        pred_quantiles = None
        if quantiles:
            pred_quantiles = self._forecaster.predict_quantiles(
                alpha=quantiles, X=X_future, fh=fh
            )

        response: ForecastResponse = to_response(pred, request, quantiles=pred_quantiles)
        return response
