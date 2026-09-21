"""In-memory inference metrics for the TServe server.

TServe is a time-series foundation-model inference server. This package
exposes ``Stats``: a thread-safe collector. Bootstrap calls
``register`` after each ``load`` and ``warmup``; ``Scheduler.run``
calls ``record``. ``GET /stats`` serializes ``snapshot()`` via
``StatsResult.model_validate``.

Stats keys are **loaded model ids** (the same ids ``GET /models``
lists), not executor plugin names. This package does not convert
frames — it never sees wire converters or sktime converters.

See Also
--------
tserve.logging.stats.Stats
    ``register``, ``record``, and ``snapshot``.
tserve.types.models.StatsResult
    Pydantic schema for the ``GET /stats`` payload.
"""

from tserve.logging.stats import Stats

__all__ = ["Stats"]
