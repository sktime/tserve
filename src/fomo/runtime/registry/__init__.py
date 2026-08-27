"""Model catalogs and resolution of ``load_models`` items.

``SKTIME_REGISTRY`` is a catalog of ids the server *can* load.
``GET /models`` lists **loaded** models only; nothing is instantiated
until ``bootstrap(load_models)`` / ``--load-models``. Registry ids
(``naive``, ``chronos-2``, …) are not executor names (``sktime``,
``pytorch-forecasting``, ``custom``).

See Also
--------
fomo.runtime.registry.resolver.resolve_model
    String, ``Path``, or ``(id, object)`` → ``ModelInfo``.
fomo.runtime.registry.sktime_registry.SKTIME_REGISTRY
    sktime craft-spec catalog.
"""

from fomo.runtime.registry.base import BASE_REGISTRY_TYPE
from fomo.runtime.registry.sktime_registry import SKTIME_REGISTRY
from fomo.runtime.registry.resolver import resolve_model

__all__ = ["resolve_model", "BASE_REGISTRY_TYPE", "SKTIME_REGISTRY"]
