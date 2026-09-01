# Architecture

FoMo loads selected models once at process start, then dispatches each forecast to the executor for that loaded id.

## Server path

`fomo serve` / [`Server(...)`][fomo.server.serve.Server] → [`bootstrap(load_models)`][fomo.runtime.bootstrap.bootstrap] → FastAPI routes → [`Scheduler.run`][fomo.scheduling.scheduler.Scheduler.run] → [`Executor.predict`][fomo.runtime.executors.base.Executor.predict].

1. **CLI / `Server`.** Flags and constructor args become a `load_models` list. Optional `models_dir` rewrites matching zip stems to `Path`. `bootstrap` runs inside [`Server.__init__`][fomo.server.serve.Server].
2. **`bootstrap`.** For each item: [`resolve_model`][fomo.runtime.registry.resolver.resolve_model] → [`create_executor(info.executor)`][fomo.runtime.executors.plugins.create_executor] → `load` → `warmup` → [`stats.register`][fomo.logging.stats.Stats]. Result is a [`Runtime`][fomo.runtime.bootstrap.Runtime] (`executors`, `models`, `stats`, `Scheduler`).
3. **Routes.** `GET /` serves the dashboard. `GET /health`, `/models`, `/stats`. JSON `POST /forecast` coerces with [`coerce_request`][fomo.types.converters.coerce_request]. Bytes `POST /forecast/bytes` rebuilds a coerced request with [`decode_request`][fomo.types.converters.decode_request]. Both call `scheduler.run`. Routes assign `request_id` (UUID).
4. **`Scheduler`.** Looks up `request.model` in the loaded-executors dict (loaded **id**, not executor name). Missing ids raise `RuntimeError`. On a hit, calls `executor.predict` and records latency in a `finally` block (including failures).
5. **Executor.** Implementations only see [`CoercedForecastRequest`][fomo.types.models.CoercedForecastRequest] / [`CoercedForecastResponse`][fomo.types.models.CoercedForecastResponse]. [`SktimeExecutor`][fomo.runtime.executors.sktime.executor.SktimeExecutor] maps the coerced request onto sktime `(y, X, fh)` via [`from_request`][fomo.runtime.executors.sktime.converters.from_request], then `fit` / `predict` (and optional `predict_quantiles`). [`PytorchForecastingExecutor`][fomo.runtime.executors.pytorch_forecasting.executor.PytorchForecastingExecutor] raises `NotImplementedError`.

JSON responses convert narwhals tables with `to_dict(as_series=False)`. The bytes path uses [`encode_response`][fomo.types.converters.encode_response] and [`pack_envelope`][fomo.types.converters.pack_envelope]. [`to_response`][fomo.runtime.executors.sktime.converters.to_response] sets `request_id=""`; server routes fill the real id.

## Client path

[`Client.forecast`][fomo.client.client.Client.forecast] → [`coerce_request`][fomo.types.converters.coerce_request] → [`encode_request`][fomo.types.converters.encode_request] → [`BaseTransport.forecast`][fomo.client.transports.base.BaseTransport.forecast] → [`decode_response`][fomo.types.converters.decode_response] → restore native frames.

`Client` does not POST JSON `/forecast`. The default transport is [`HttpTransport`][fomo.client.transports.http.HttpTransport], which POSTs multipart + Arrow to `/forecast/bytes` and unpacks the envelope with [`unpack_envelope`][fomo.types.converters.unpack_envelope]. Status methods wrap `GET /health`, `/models`, `/stats`.

## Two conversion layers

| layer | module | job |
| --- | --- | --- |
| Wire converters | [`fomo.types.converters`][fomo.types.converters] | native frames ↔ narwhals ↔ Arrow IPC ↔ `FOMO` envelope |
| sktime converters | [`fomo.runtime.executors.sktime.converters`][fomo.runtime.executors.sktime.converters] | coerced request ↔ `y`, `X`, `X_future`, `fh` |

User-facing frames are [`ForecastRequest`][fomo.types.models.ForecastRequest] / [`ForecastResponse`][fomo.types.models.ForecastResponse]. Coerced models are internal narwhals. Executors and the scheduler only see coerced.

[`HttpTransport`][fomo.client.transports.http.HttpTransport] and JSON `/forecast` do not import each other. A third transport is a new [`BaseTransport`][fomo.client.transports.base.BaseTransport] subclass, not a runtime change.
