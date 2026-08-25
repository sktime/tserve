from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any
from pathlib import Path


def _resolve_from_registry(item: str) -> ModelInfo:
    if item in SKTIME_REGISTRY:
        return ModelInfo(id=item, executor="sktime", source="registry")

    raise ValueError(f"unknown registry {item!r}, choose one of: {', '.join(SKTIME_REGISTRY.keys())}")


def _resolve_from_path(item: Path) -> ModelInfo:
    if item.suffix == ".zip":
        return ModelInfo(id=item.stem, executor="sktime", source="directory")

    raise ValueError(f"unknown file {item!r}, must be a zip file")


def _resolve_from_object(item: tuple[str, Any]) -> ModelInfo:
    model_id, obj = item

    if type(obj).__module__.startswith("sktime."):
        return ModelInfo(id=model_id, executor="sktime", source="object")

    raise TypeError(f"expected sktime object, got {type(obj).__name__}")


def resolve_model(item: str | Path | tuple[str, Any]) -> ModelInfo:
    if isinstance(item, str):
        return _resolve_from_registry(item)

    if isinstance(item, Path):
        return _resolve_from_path(item)

    return _resolve_from_object(item)
