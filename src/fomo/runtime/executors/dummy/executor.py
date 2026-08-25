from datetime import datetime, timedelta
from typing import Any

import narwhals as nw

from fomo.runtime.executors.plugins import register
from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


@register("dummy")
class DummyExecutor:
    def __init__(self) -> None:
        self._info: ModelInfo | None = None
        self.load_s: float | None = None
        self.warmup_s: float | None = None

    def load(self, info: ModelInfo, model: Any) -> None:
        self._info = info
        self.load_s = 0.0
        self.warmup_s = 0.0

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        history = request.history.to_dict(as_series=False)
        columns: dict[str, list[Any]] = {
            request.time: list[Any](range(1, request.horizon + 1)),
        }
        for col in request.target:
            columns[col] = [history[col][-1]] * request.horizon

        return CoercedForecastResponse(
            predictions=nw.from_dict(columns, backend="pyarrow"),
            model=request.model,
            request_id="",
            quantiles=None,
        )
