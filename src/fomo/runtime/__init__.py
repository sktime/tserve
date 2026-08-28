"""Load models once and hold the process-local executor map.

FoMo is a time-series foundation-model inference server. Models load
once at process start. This package is that start path: resolve a
catalog id, zip, or in-process forecaster; construct an executor; load;
warmup; register stats. Forecast dispatch lives in ``fomo.scheduling``,
not here.

Executors only see ``CoercedForecastRequest`` /
``CoercedForecastResponse``. Two conversion layers (spellings differ on
purpose):

* Wire **converters** (``fomo.types.converters``): native frames ↔
  narwhals ↔ Arrow IPC ↔ FOMO envelope.
* sktime **convertors** (``fomo.runtime.executors.sktime.convertors``):
  coerced request ↔ ``(y, X, X_future, fh)`` and back.

``GET /models`` lists **loaded** models only. Registry ids (``naive``,
``chronos-2``, …) are not executor names (``sktime``,
``pytorch-forecasting``, ``custom``). ``SKTIME_REGISTRY`` is a catalog;
nothing loads until ``bootstrap(load_models)`` / ``--load-models``.

FoMo has no custom exception classes. ``HealthError`` is a Pydantic
payload, not an exception.

See Also
--------
fomo.runtime.bootstrap
    ``Runtime`` handle and ``bootstrap(load_models)``.
fomo.runtime.executors
    Executor ABC, plugin registry, and ``create_executor``.
fomo.runtime.registry
    ``resolve_model`` and the sktime catalog.
fomo.scheduling.scheduler.Scheduler
    Routes a coerced request to a loaded executor.
"""
