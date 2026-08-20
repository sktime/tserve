from typing import Any

import pandas as pd
from sktime.forecasting.base import ForecastingHorizon

from fomo.types import ForecastRequest

_WARMUP_Y = pd.DataFrame({"y": [0.0, 1.0, 2.0]})
_WARMUP_FH = ForecastingHorizon([1], is_relative=True)


def warmup_forecaster(forecaster: Any) -> None:
    forecaster.fit(_WARMUP_Y, fh=_WARMUP_FH)
    forecaster.predict()


def apply_model_config(forecaster: Any, request: ForecastRequest) -> None:
    freq = request.freq or (request.params or {}).get("freq")
    if freq is not None and hasattr(forecaster, "freq"):
        forecaster.freq = freq
