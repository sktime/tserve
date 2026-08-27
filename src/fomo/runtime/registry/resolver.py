from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any
from pathlib import Path


def _resolve_from_registry(item: str) -> ModelInfo:
    if item in SKTIME_REGISTRY:
        return ModelInfo(id=item, executor="sktime", source="registry")

    raise ValueError(
        f"unknown model {item!r}; known registry ids: {', '.join(SKTIME_REGISTRY.keys())}"
    )


def _resolve_from_path(item: Path) -> ModelInfo:
    if item.suffix == ".zip":
        return ModelInfo(id=item.stem, executor="sktime", source="directory")

    raise ValueError(f"{item} is not a saved sktime model; expected a .zip file")


def _resolve_from_object(item: tuple[str, Any]) -> ModelInfo:
    from sktime.forecasting.base import BaseForecaster

    model_id, obj = item

    if isinstance(obj, BaseForecaster):
        return ModelInfo(id=model_id, executor="sktime", source="object")

    raise TypeError(
        f"load_models entry {model_id!r} must be a sktime forecaster, "
        f"got {type(obj).__name__}"
    )


def resolve_model(item: str | Path | tuple[str, Any]) -> ModelInfo:
    if isinstance(item, str):
        return _resolve_from_registry(item)

    if isinstance(item, Path):
        return _resolve_from_path(item)

    return _resolve_from_object(item)
