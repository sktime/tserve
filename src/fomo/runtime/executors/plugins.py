from collections.abc import Callable
from typing import TypeVar

from fomo.runtime.executors.base import Executor

_PLUGINS: dict[str, type[Executor]] = {}
T = TypeVar("T", bound=type[Executor])


def register(name: str) -> Callable[[T], T]:
    def decorator(cls: T) -> T:
        _PLUGINS[name] = cls
        return cls

    return decorator


def available_executors() -> tuple[str, ...]:
    return tuple(sorted(_PLUGINS))


def create_executor(name: str) -> Executor:
    try:
        cls = _PLUGINS[name]
    except KeyError as exc:
        known = ", ".join(available_executors()) or "(none registered)"
        raise ValueError(f"unknown executor {name!r}, choose one of: {known}") from exc
    return cls()
