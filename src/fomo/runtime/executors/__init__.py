"""Executor plugins: ABC, lazy construction, and name registry.

Executor names (``sktime``, ``pytorch-forecasting``, ``custom``) are not
registry model ids (``naive``, ``chronos-2``, …). Executors only see
``CoercedPredictRequest`` / ``CoercedPredictResponse``.

See Also
--------
fomo.runtime.executors.base.Executor
    ``load`` / ``warmup`` / ``predict`` contract.
fomo.runtime.executors.plugins.create_executor
    Lazy-import a plugin by executor name.
"""

from fomo.runtime.executors.base import Executor
from fomo.runtime.executors.plugins import (
    available_executors,
    create_executor,
    register,
)

__all__ = [
    "Executor",
    "available_executors",
    "create_executor",
    "register",
]
