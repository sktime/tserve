# Errors

FoMo has no custom exception types. Validators raise `ValueError`; Pydantic surfaces that as `ValidationError`.

## HTTP `POST /forecast`

| status | when | body |
| --- | --- | --- |
| **400** | coerce or predict failed (id not loaded, missing columns, estimator error) | `{"detail": {"error": "<message>", "code": "request_failed", "request_id": "<uuid>"}}` |
| **422** | body failed [`ForecastRequest`][fomo.types.models.ForecastRequest] (missing `past` / `fh`, `fh <= 0`, bad table shape) | FastAPI validation error |

`POST /forecast/bytes` uses the same HTTP 400 wrapping.

## Python `Client`

HTTP status >= 400 becomes `RuntimeError` with `detail["error"]` when that field exists. Connection and timeout errors are `httpx.RequestError`. Local construction / coerce failures are `ValidationError` before anything is sent.

## Construction

These fail before uvicorn starts (CLI) or during [`Server`][fomo.server.serve.Server] construction:

| exception | when |
| --- | --- |
| `ValueError` | unknown registry id, non-`.zip` path, duplicate loaded id |
| `TypeError` | `(id, object)` is not a sktime `BaseForecaster` |
| `ImportError` | executor extra not installed |
| `OSError` | `models_dir` cannot be listed |
