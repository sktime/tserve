"""Model catalogs and resolution of ``model`` items.

``SKTIME_REGISTRY`` is a catalog of ids the server *can* load.
``GET /models`` lists **loaded** models only; nothing is instantiated
until ``bootstrap(model)`` / leftover CLI positionals. Registry ids
(``naive``, ``chronos-2``, …) are not executor names (``sktime``,
``pytorch-forecasting``, ``custom``).

See Also
--------
tserve.runtime.registry.resolver.resolve_model
    String, ``Path``, ``(id, spec)``, or ``(id, object)`` → ``ModelInfo``.
tserve.runtime.registry.sktime_registry.SKTIME_REGISTRY
    sktime craft-spec catalog.
"""

from tserve.runtime.registry.base import BASE_REGISTRY_TYPE
from tserve.runtime.registry.resolver import resolve_model
from tserve.runtime.registry.sktime_registry import SKTIME_REGISTRY

__all__ = ["BASE_REGISTRY_TYPE", "SKTIME_REGISTRY", "resolve_model"]
