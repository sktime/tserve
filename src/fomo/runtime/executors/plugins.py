import importlib
from collections.abc import Callable
from typing import TypeVar

from fomo.runtime.executors.base import Executor

_PLUGINS: dict[str, type[Executor]] = {}
T = TypeVar("T", bound=type[Executor])

_EXECUTOR_MODULES = {
    "dummy": "fomo.runtime.executors.dummy.executor",
    "sktime": "fomo.runtime.executors.sktime.executor",
    "pytorch-forecasting": "fomo.runtime.executors.pytorch_forecasting.executor",
}


def register(name: str) -> Callable[[T], T]:
    def decorator(cls: T) -> T:
        _PLUGINS[name] = cls
        return cls

    return decorator


def available_executors() -> tuple[str, ...]:
    return tuple(sorted(set(_PLUGINS) | set(_EXECUTOR_MODULES)))


def _ensure_registered(name: str) -> None:
    if name in _PLUGINS:
        return
    module = _EXECUTOR_MODULES.get(name)
    if module is None:
        return
    try:
        importlib.import_module(module)
    except ImportError as exc:
        extra = name
        raise ImportError(
            f"executor {name!r} requires the {extra} extra; "
            f"install with pip install 'fomo[{extra}]'"
        ) from exc


def create_executor(name: str) -> Executor:
    _ensure_registered(name)
    try:
        cls = _PLUGINS[name]
    except KeyError as exc:
        known = ", ".join(available_executors()) or "(none registered)"
        raise ValueError(f"unknown executor {name!r}, choose one of: {known}") from exc
    return cls()
