"""Turn a ``load_models`` item into listing-only ``ModelInfo``.

Does not instantiate a forecaster. Registry ids become
``source="registry"``; ``.zip`` paths become ``source="directory"``
(id = stem); ``(id, BaseForecaster)`` tuples become ``source="object"``.
All three paths currently set ``executor="sktime"``.

See Also
--------
fomo.runtime.registry.sktime_registry.SKTIME_REGISTRY
    Catalog consulted for string ids.
fomo.types.models.ModelInfo
    Listing row (``id``, ``executor``, ``source``).
"""

from fomo.types import ModelInfo
from fomo.runtime.registry import SKTIME_REGISTRY
from typing import Any
from pathlib import Path


def _resolve_from_registry(item: str) -> ModelInfo:
    """Look up a catalog id in ``SKTIME_REGISTRY``.

    Parameters
    ----------
    item : str
        Registry id (for example ``naive``), not an executor name.

    Returns
    -------
    ModelInfo
        ``id=item``, ``executor="sktime"``, ``source="registry"``.

    Raises
    ------
    ValueError
        If ``item`` is not a key of ``SKTIME_REGISTRY``. The message
        lists known registry ids.
    """
    if item in SKTIME_REGISTRY:
        return ModelInfo(id=item, executor="sktime", source="registry")

    raise ValueError(
        f"unknown model {item!r}; known registry ids: {', '.join(SKTIME_REGISTRY.keys())}"
    )


def _resolve_from_path(item: Path) -> ModelInfo:
    """Accept a saved sktime ``.zip`` path (suffix check only).

    The file is not opened here; ``SktimeExecutor.load`` calls
    ``sktime.base.load``. Existence is not checked.

    Parameters
    ----------
    item : pathlib.Path
        Path whose suffix must be ``.zip``. ``id`` is ``item.stem``.

    Returns
    -------
    ModelInfo
        ``id=item.stem``, ``executor="sktime"``, ``source="directory"``.

    Raises
    ------
    ValueError
        If ``item.suffix`` is not ``.zip``.
    """
    if item.suffix == ".zip":
        return ModelInfo(id=item.stem, executor="sktime", source="directory")

    raise ValueError(f"{item} is not a saved sktime model; expected a .zip file")


def _resolve_from_object(item: tuple[str, Any]) -> ModelInfo:
    """Accept an in-process sktime ``BaseForecaster``.

    Parameters
    ----------
    item : (str, any)
        ``(model_id, obj)``. ``obj`` must be a sktime ``BaseForecaster``.

    Returns
    -------
    ModelInfo
        ``id=model_id``, ``executor="sktime"``, ``source="object"``.

    Raises
    ------
    TypeError
        If ``obj`` is not a ``BaseForecaster``. Message includes
        ``model_id`` and ``type(obj).__name__``.
    """
    from sktime.forecasting.base import BaseForecaster

    model_id, obj = item

    if isinstance(obj, BaseForecaster):
        return ModelInfo(id=model_id, executor="sktime", source="object")

    raise TypeError(
        f"load_models entry {model_id!r} must be a sktime forecaster, "
        f"got {type(obj).__name__}"
    )


def resolve_model(item: str | Path | tuple[str, Any]) -> ModelInfo:
    """Dispatch a load-models item to registry, path, or object resolution.

    Parameters
    ----------
    item : str or Path or (str, any)
        String → ``SKTIME_REGISTRY`` lookup. ``Path`` → ``.zip`` only.
        Tuple ``(id, obj)`` → must be a sktime ``BaseForecaster``.

    Returns
    -------
    ModelInfo
        Listing row used by bootstrap and ``GET /models``. Does not
        mean the model is loaded yet.

    Raises
    ------
    ValueError
        Unknown registry id, or path that is not a ``.zip``.
    TypeError
        Tuple whose object is not a sktime ``BaseForecaster``.
    """
    if isinstance(item, str):
        return _resolve_from_registry(item)

    if isinstance(item, Path):
        return _resolve_from_path(item)

    return _resolve_from_object(item)
