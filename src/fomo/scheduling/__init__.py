"""Dispatch coerced forecasts from HTTP routes to loaded executors.

FoMo is a time-series foundation-model inference server. ``Scheduler``
sits between HTTP routes and ``Executor.predict``. It looks up
``request.model`` — a **loaded model id**, not an executor name — in
the executors dict, times the predict call with ``perf_counter``, and
always records via ``stats.record`` in a ``finally`` block so failed
calls still get latency.

Executors and the scheduler only see ``CoercedForecastRequest``. This
package does not convert frames: wire conversion lives in
``fomo.types.converters``; sktime ``(y, X, fh)`` mapping lives in
``fomo.runtime.executors.sktime.convertors``.

See Also
--------
fomo.scheduling.scheduler.Scheduler
    Lookup, timing, and ``stats.record``.
fomo.types.models.CoercedForecastRequest
    Internal request type passed through unchanged.
"""
