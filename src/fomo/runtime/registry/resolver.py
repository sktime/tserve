from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any


def _resolve_from_registry(item: str) -> ModelInfo:
    if item in SKTIME_REGISTRY:
        return ModelInfo(alias=item, executor="sktime", source="registry")

    raise ValueError(f"unknown registry {item!r}, choose one of: {', '.join(SKTIME_REGISTRY.keys())}")


def _resolve_from_object(item: Any) -> ModelInfo:
    if not (isinstance(item, tuple) and len(item) == 2):
        raise TypeError(f"expected tuple of (alias, object), got {type(item).__name__}")

    alias, obj = item

    if type(obj).__module__.startswith("sktime."):
        return ModelInfo(alias=alias, executor="sktime", source="object")

    raise TypeError(f"expected sktime object, got {type(obj).__name__}")


def resolve_model(item: str | tuple[str, Any]) -> ModelInfo:
    if isinstance(item, str):
        return _resolve_from_registry(item)

    return _resolve_from_object(item)
