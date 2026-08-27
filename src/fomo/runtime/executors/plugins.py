"""Map executor names to classes, importing extras only when requested.

Built-in names in ``_EXECUTOR_MODULES`` are not loaded until
``create_executor`` (or an explicit import) runs. ``@register`` also
stores custom subclasses. Executor names are not registry model ids.

See Also
--------
fomo.runtime.executors.base.Executor
    Class each plugin must subclass.
"""

import importlib
from collections.abc import Callable
from typing import TypeVar

from fomo.runtime.executors.base import Executor

_PLUGINS: dict[str, type[Executor]] = {}
T = TypeVar("T", bound=type[Executor])

_EXECUTOR_MODULES = {
    "sktime": "fomo.runtime.executors.sktime.executor",
    "pytorch-forecasting": "fomo.runtime.executors.pytorch_forecasting.executor",
}


def register(name: str) -> Callable[[T], T]:
    """Register an ``Executor`` subclass under an executor name.

    The decorated class is stored in ``_PLUGINS`` and returned unchanged.
    ``create_executor(name)`` then instantiates it with no arguments.

    Parameters
    ----------
    name : str
        Plugin name (``sktime``, ``pytorch-forecasting``, or a custom
        id). Not a registry model id such as ``naive``.

    Returns
    -------
    callable
        Class decorator that records ``cls`` in ``_PLUGINS[name]``.
    """
    def decorator(cls: T) -> T:
        """Store ``cls`` in ``_PLUGINS`` and return it.

        Parameters
        ----------
        cls : type of Executor
            Executor subclass to register.

        Returns
        -------
        type of Executor
            ``cls`` unchanged.
        """
        _PLUGINS[name] = cls
        return cls

    return decorator


def available_executors() -> tuple[str, ...]:
    """Return sorted executor names from plugins and built-in modules.

    Returns
    -------
    tuple of str
        Union of ``_PLUGINS`` keys and ``_EXECUTOR_MODULES`` keys,
        sorted. Includes names whose extra is not installed yet.
    """
    return tuple(sorted(set(_PLUGINS) | set(_EXECUTOR_MODULES)))


def _ensure_registered(name: str) -> None:
    """Import the built-in executor module for ``name`` if needed.

    No-op when ``name`` is already in ``_PLUGINS`` or is not a built-in
    module name. Unknown names are left for ``create_executor`` to reject.

    Parameters
    ----------
    name : str
        Executor plugin name.

    Raises
    ------
    ImportError
        If the built-in module import fails. The message tells the
        caller to ``pip install 'fomo[{name}]'`` (``name`` is used as
        the extra, e.g. ``sktime`` or ``pytorch-forecasting``).
    """
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
    """Construct a new executor instance for a plugin name.

    Lazy-imports the built-in module when ``name`` is in
    ``_EXECUTOR_MODULES`` and not yet registered.

    Parameters
    ----------
    name : str
        Executor name (``sktime``, ``pytorch-forecasting``, or a name
        passed to ``@register``). Not a catalog id such as ``naive``.

    Returns
    -------
    Executor
        ``cls()`` for the registered subclass (no constructor args).

    Raises
    ------
    ImportError
        If the built-in extra cannot be imported (from
        ``_ensure_registered``).
    ValueError
        If ``name`` is not registered after import. The message lists
        ``available_executors()``, or ``(none registered)`` if that
        tuple is empty.
    """
    _ensure_registered(name)
    try:
        cls = _PLUGINS[name]
    except KeyError as exc:
        known = ", ".join(available_executors()) or "(none registered)"
        raise ValueError(f"unknown executor {name!r}, choose one of: {known}") from exc
    return cls()
