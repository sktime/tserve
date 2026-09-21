"""Turn a ``model`` item into listing-only ``ModelInfo``.

Does not instantiate a forecaster. Registry ids become
``source="registry"``; ``.zip`` paths become ``source="directory"``
(id = stem); ``(id, spec)`` tuples become ``source="craft"``;
``(id, BaseForecaster)`` tuples become ``source="object"``.
All four paths currently set ``executor="sktime"``.

See Also
--------
tserve.runtime.registry.sktime_registry.SKTIME_REGISTRY
    Catalog consulted for string ids.
tserve.types.models.ModelInfo
    Listing row (``id``, ``executor``, ``source``).
"""

from pathlib import Path
from typing import Any

from tserve.runtime.registry.sktime_registry import SKTIME_REGISTRY
from tserve.types import ModelInfo

_CRAFT_HINT = (
    " To load a sktime craft spec, pass a (id, spec) pair, "
    "e.g. ('my-model', 'NaiveForecaster()')."
)


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
        lists known registry ids. Strings that look like a craft spec
        also hint to pass ``(id, spec)``.
    """
    if item in SKTIME_REGISTRY:
        return ModelInfo(id=item, executor="sktime", source="registry")

    hint = _CRAFT_HINT if "(" in item else ""
    raise ValueError(
        f"unknown model {item!r}; "
        f"known registry ids: {', '.join(SKTIME_REGISTRY.keys())}.{hint}"
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
    """Accept a craft spec string or an in-process ``BaseForecaster``.

    Parameters
    ----------
    item : (str, any)
        ``(model_id, obj)``. ``obj`` is a non-empty craft spec string
        or a sktime ``BaseForecaster``.

    Returns
    -------
    ModelInfo
        ``id=model_id``, ``executor="sktime"``. ``source`` is
        ``"craft"`` for a spec string, ``"object"`` for a forecaster.

    Raises
    ------
    ValueError
        If ``obj`` is a string that is empty or whitespace-only.
    TypeError
        If ``obj`` is neither a ``str`` nor a ``BaseForecaster``.
        Message includes ``model_id`` and ``type(obj).__name__``.
    """
    from sktime.forecasting.base import BaseForecaster

    model_id, obj = item

    if isinstance(obj, str):
        if not obj.strip():
            raise ValueError(f"model entry {model_id!r} has an empty craft spec")
        return ModelInfo(id=model_id, executor="sktime", source="craft")

    if isinstance(obj, BaseForecaster):
        return ModelInfo(id=model_id, executor="sktime", source="object")

    raise TypeError(
        f"model entry {model_id!r} must be a sktime forecaster "
        f"or a craft spec string, got {type(obj).__name__}"
    )


def resolve_model(item: str | Path | tuple[str, Any]) -> ModelInfo:
    """Dispatch a model item to registry, path, craft, or object.

    Parameters
    ----------
    item : str or Path or (str, any)
        String → ``SKTIME_REGISTRY`` lookup. ``Path`` → ``.zip`` only.
        Tuple ``(id, spec)`` → non-empty craft spec string.
        Tuple ``(id, obj)`` → must be a sktime ``BaseForecaster``.

    Returns
    -------
    ModelInfo
        Listing row used by bootstrap and ``GET /models``. Does not
        mean the model is loaded yet.

    Raises
    ------
    ValueError
        Unknown registry id, empty craft spec, or path that is not a
        ``.zip``.
    TypeError
        Tuple whose second element is neither a spec string nor a
        sktime ``BaseForecaster``.
    """
    if isinstance(item, str):
        return _resolve_from_registry(item)

    if isinstance(item, Path):
        return _resolve_from_path(item)

    return _resolve_from_object(item)
