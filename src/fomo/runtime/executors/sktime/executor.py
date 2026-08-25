import time
from typing import Any

import pandas as pd

from fomo.runtime.executors.plugins import register
from fomo.runtime.executors.sktime.convertors import from_request, to_response
from fomo.runtime.registry import SKTIME_REGISTRY
from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


@register("sktime")
class SktimeExecutor:
    def __init__(self) -> None:
        self._info: ModelInfo | None = None
        self._forecaster: Any = None
        self.load_s: float | None = None
        self.warmup_s: float | None = None

    def load(self, info: ModelInfo, model: Any) -> None:
        self._info = info

        t0 = time.perf_counter()
        if info.source == "registry":
            from sktime.registry import craft

            self._forecaster = craft(SKTIME_REGISTRY[model]["spec"])

        if info.source == "object":
            self._forecaster = model

        if info.source == "directory":
            from sktime.base import load

            self._forecaster = load(model)
        self.load_s = time.perf_counter() - t0

        t1 = time.perf_counter()
        self._forecaster.fit(pd.DataFrame({"y": [0.0, 1.0, 2.0]}))
        self._forecaster.predict(fh=[1])
        self.warmup_s = time.perf_counter() - t1

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        y, X, X_future, fh, quantiles = from_request(request)

        self._forecaster.fit(y=y, X=X, fh=fh)
        pred = self._forecaster.predict(X=X_future, fh=fh)
        pred_quantiles = None
        if quantiles:
            pred_quantiles = self._forecaster.predict_quantiles(
                alpha=quantiles, X=X_future, fh=fh
            )

        response: CoercedForecastResponse = to_response(pred, request, quantiles=pred_quantiles)
        return response
