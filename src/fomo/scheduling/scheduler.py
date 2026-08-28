"""Route a coerced forecast to the executor for its loaded model id.

See Also
--------
Scheduler
    Public class in this module.
fomo.types.models.CoercedForecastRequest
    Request type passed through to ``Executor.predict``.
"""

import time

from fomo.logging import Stats
from fomo.runtime.executors import Executor
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse


class Scheduler:
    """Dispatch a coerced forecast to a loaded executor.

    FoMo is a time-series foundation-model inference server. The
    scheduler sits between HTTP routes and ``Executor.predict``. It
    looks up ``request.model`` (a **loaded model id**, not an executor
    name) in the executors dict. Missing ids raise ``RuntimeError``
    whose message lists loaded ids, or ``"none"`` if the dict is empty.

    The predict call is timed with ``time.perf_counter``. ``stats.record``
    always runs in a ``finally`` block, so failed calls still get
    latency. The return value is the ``CoercedForecastResponse`` from
    ``executor.predict``. Executors only see coerced requests; this
    class does not convert frames (wire converters vs sktime
    convertors live elsewhere).

    There are no custom exception classes. ``HealthError`` is an
    unrelated Pydantic health payload.

    Parameters
    ----------
    executors : dict of str to Executor
        Map of **loaded model id** → executor instance, typically from
        bootstrap.
    stats : Stats
        In-memory collector. ``run`` calls ``record`` after every
        predict attempt that passed the loaded-id check.

    See Also
    --------
    fomo.types.models.CoercedForecastRequest
        Internal request; do not construct a user-facing
        ``ForecastRequest`` here.
    fomo.logging.stats.Stats
        ``record`` target; ``GET /stats`` uses ``snapshot``.
    """

    def __init__(self, executors: dict[str, Executor], stats: Stats) -> None:
        """Store ``executors`` and ``stats``. See the class docstring."""
        self._executors = executors
        self._stats = stats

    def run(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        """Look up the loaded model, predict, and record latency.

        Lookup uses ``request.model`` as a key in the executors dict.
        On a miss, raises before timing. On a hit, calls
        ``executor.predict(request)`` and returns that response.
        Predict exceptions propagate unchanged; ``finally`` still calls
        ``stats.record`` with ``ok=False`` and the elapsed seconds.

        Parameters
        ----------
        request : CoercedForecastRequest
            Coerced forecast input. Executors only see this form, not
            a user-facing ``ForecastRequest``.

        Returns
        -------
        CoercedForecastResponse
            Value returned by ``executor.predict``.

        Raises
        ------
        RuntimeError
            If ``request.model`` is not loaded. The message is
            ``model {id!r} is not loaded on this server (loaded: …)``
            with comma-separated ``repr`` of sorted loaded ids, or
            ``none`` if none are loaded.
        Exception
            Errors from ``executor.predict`` propagate unchanged
            (after ``stats.record`` with ``ok=False``).
        """
        executor = self._executors.get(request.model)
        if executor is None:
            loaded = ", ".join(repr(name) for name in sorted(self._executors)) or "none"
            raise RuntimeError(
                f"model {request.model!r} is not loaded on this server "
                f"(loaded: {loaded})"
            )

        started = time.perf_counter()
        ok = False
        try:
            response = executor.predict(request)
            ok = True
            return response
        finally:
            self._stats.record(request.model, time.perf_counter() - started, ok)
