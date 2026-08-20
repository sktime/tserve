from typing import Any

from sktime.registry import craft

from fomo.runtime.registry import get_registry_craft


def load_forecaster(alias: str) -> Any:
    return craft(get_registry_craft(alias))
