from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any


def _resolve_from_registry(item: str) -> ModelInfo:
    if item in SKTIME_REGISTRY:
        return ModelInfo(alias=item, executor="sktime", source="registry")

    raise ValueError(f"unknown registry {item!r}, choose one of: {', '.join(SKTIME_REGISTRY.keys())}")


def _resolve_from_object(item: Any) -> ModelInfo:
    if type(item).__module__.startswith("sktime."):
        return ModelInfo(alias=str(item), executor="sktime", source="object")

    raise TypeError(f"expected sktime object, got {type(item).__name__}")


def resolve_model(item: Any) -> ModelInfo:
    if isinstance(item, str):
        return _resolve_from_registry(item)

    return _resolve_from_object(item)
