from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any


def _resolve_from_registry(item: str):
    if item in SKTIME_REGISTRY:
        return ModelInfo(alias=item, executor="sktime", source="registry")

    raise ValueError(f"unknown registry {item!r}, choose one of: {', '.join(SKTIME_REGISTRY.keys())}")


def resolve_model(item: Any) -> ModelInfo:
    if isinstance(item, str):
        return _resolve_from_registry(item)

    raise TypeError(f"expected str, got {type(item).__name__}")
