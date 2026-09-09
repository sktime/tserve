# Errors

FoMo defines no exception types of its own. The server answers with HTTP
status codes, and the Python side raises built-ins plus Pydantic
`ValidationError`.

## Predict requests

| status | when |
| --- | --- |
| **422** | the body does not match [`PredictRequest`][fomo.types.models.PredictRequest]: `past` or `fh` missing, `fh` not `> 0`, a table that is neither table shape, columns of unequal length, a row narrower than `columns` |
| **400** | the body was accepted but the request failed: the `model` id is not loaded, `past` or `future` lacks the selected columns, target inference left nothing to forecast, or the estimator itself raised |
| **405** | wrong method, such as `GET /predict` |

The split is where the failure happens. **422** is FastAPI rejecting the
JSON body before the handler runs, so the body is the usual FastAPI list of
field errors. **400** is the handler wrapping everything after that:

```json
{
  "detail": {
    "error": "model 'chronos-2' is not loaded on this server (loaded: 'chronos-bolt', 'ttm-r3')",
    "code": "request_failed",
    "request_id": "…"
  }
}
```

An id that is missing from `GET /models` is 400, not 404. Missing columns read
`past is missing columns: ['sales'] (available: ['timestamp', 'value'])`.
Estimator failures keep the message the estimator raised, so a series shorter
than a model's context length surfaces here too.

`POST /predict/bytes` behaves the same way, with 422 reserved for a missing
`metadata` field or `past` file.

A **404** with `{"detail": "Not Found"}` is not a predict error: that path
does not exist on this process. Check the URL, the port, and that you are
posting to `/predict` — there is no version prefix.

## Python client

| raised | when |
| --- | --- |
| `ValidationError` | local, before any HTTP call: unsupported table shape, `fh` not `> 0`, missing time or target column, empty inferred target |
| `RuntimeError` | the server answered 400 or higher; the message is `detail["error"]` when present, else the raw body |
| `httpx.RequestError` | connection refused, DNS failure, or timeout (default 60 s, set `timeout=` on `Client`) |
| `ValueError` | the response envelope is truncated, has wrong magic bytes, or an unsupported version |

`RuntimeError` is deliberately flat: the server-side type is gone by then, so
read the message. Local `ValidationError`s never reach the network, which is
why a wrong table shape fails instantly while an unloaded id needs a round
trip.

The one surprising local failure is a pandas frame whose time axis is only the
index. `time` then resolves to the first real column, target inference finds
nothing left, and the request fails before it is sent. Call `reset_index()`
first — see [Use an indexed pandas frame](../client/python.md#use-an-indexed-pandas-frame).

## Startup

These stop [`Server`][fomo.server.serve.Server] construction, which means the
CLI exits before uvicorn binds the port:

| exception | when |
| --- | --- |
| `ValueError` | unknown registry id (the message lists the known ids), a duplicate id in `load_models`, or a path that is not a `.zip` |
| `TypeError` | an `(id, object)` pair whose object is not a sktime `BaseForecaster` |
| `ImportError` | the executor's extra is not installed |
| `OSError` | `models_dir` does not exist or cannot be listed |

Whatever an estimator raises while loading or warming up propagates unchanged,
so a failed Hugging Face download stops startup with that library's error. A
[family extra](../models/index.md#dependencies) or image tag that matches
the ids you load is what avoids this.
