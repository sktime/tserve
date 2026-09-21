"""Load models once and hold the process-local executor map.

TServe is a time-series foundation-model inference server. Models load
once at process start. This package is that start path: resolve a
catalog id, zip, or in-process forecaster; construct an executor; load;
warmup; register stats. Predict dispatch lives in ``tserve.scheduling``,
not here.

Executors only see ``CoercedPredictRequest`` /
``CoercedPredictResponse``. Two conversion layers:

* Wire converters (``tserve.types.converters``): native frames ↔
  narwhals ↔ Arrow IPC ↔ TServe envelope.
* sktime converters (``tserve.runtime.executors.sktime.converters``):
  coerced request ↔ ``(y, X, X_future, fh)`` and back.

``GET /models`` lists **loaded** models only. Registry ids (``naive``,
``chronos-2``, …) are not executor names (``sktime``,
``pytorch-forecasting``, ``custom``). ``SKTIME_REGISTRY`` is a catalog;
nothing loads until ``bootstrap(model)`` / ``--model``.

TServe has no custom exception classes. ``HealthError`` is a Pydantic
payload, not an exception.

See Also
--------
tserve.runtime.bootstrap
    ``Runtime`` handle and ``bootstrap(model)``.
tserve.runtime.executors
    Executor ABC, plugin registry, and ``create_executor``.
tserve.runtime.registry
    ``resolve_model`` and the sktime catalog.
tserve.scheduling.scheduler.Scheduler
    Routes a coerced request to a loaded executor.
"""
