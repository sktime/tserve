# Errors

FoMo has no custom exception types. [`HealthError`][fomo.types.models.HealthError] is a Pydantic payload nested under [`HealthResult.error`][fomo.types.models.HealthResult], not something handlers raise. Validators raise `ValueError`; Pydantic constructors expose that as `ValidationError`.

## HTTP JSON `POST /forecast`

| status | when | body |
| --- | --- | --- |
| **400** | Coerce or predict failed (unknown loaded id, missing columns, estimator error, `NotImplementedError`) | `{"detail": {"error": "<message>", "code": "request_failed", "request_id": "<uuid>"}}` |
| **422** | Body failed [`ForecastRequest`][fomo.types.models.ForecastRequest] validation (invalid JSON types, missing `past` / `fh`, `fh <= 0`, unsupported table shape) | FastAPI / Pydantic validation error |

There is no 503 for forecast failures. [`Scheduler.run`][fomo.scheduling.scheduler.Scheduler.run] raises `RuntimeError` for an id that is not loaded; the JSON route wraps that as 400 `request_failed`.

`POST /forecast/bytes` uses the same HTTP 400 wrapping. JSON parse failures on the `metadata` form field are also 400.

## Python `Client`

[`HttpTransport`][fomo.client.transports.http.HttpTransport] turns HTTP status >= 400 into `RuntimeError`. If the JSON `detail` is a dict, the message is `detail["error"]`. Otherwise the message is `str(detail)` or the raw text body. Connection and timeout errors are `httpx.RequestError`.

[`Client.forecast`][fomo.client.client.Client.forecast] can also raise `ValidationError` locally if [`ForecastRequest`][fomo.types.models.ForecastRequest] construction or [`coerce_request`][fomo.types.converters.coerce_request] fails before the request is sent.

## Construction / bootstrap

These fail before uvicorn starts (CLI) or during [`Server`][fomo.server.serve.Server] construction:

| exception | when |
| --- | --- |
| `ValueError` | unknown registry id, non-`.zip` path, duplicate loaded id, unknown executor name |
| `TypeError` | `(id, object)` whose object is not a sktime `BaseForecaster` |
| `ImportError` | executor extra not installed (`pip install 'fomo[{name}]'`) |
| `NotImplementedError` | [`PytorchForecastingExecutor`][fomo.runtime.executors.pytorch_forecasting.executor.PytorchForecastingExecutor] `load` / `warmup` / `predict` |
| `OSError` | `models_dir` cannot be listed |
