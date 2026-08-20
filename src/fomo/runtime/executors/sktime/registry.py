from typing import Any

import pandas as pd
from sktime.registry import craft

from fomo.runtime.registry import get_registry_craft


def load_forecaster(alias: str) -> Any:
    estimator = craft(get_registry_craft(alias))

    estimator.fit(pd.DataFrame({"y": [0.0, 1.0, 2.0]}))
    estimator.predict(fh=[1])

    return estimator
