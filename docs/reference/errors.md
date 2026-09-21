# Errors

TServe defines no exception types of its own. The server answers with HTTP status codes, and the Python side raises built-ins plus Pydantic `ValidationError`.

## Predict requests

| status | when |
| --- | --- |
| **422** | the body does not match [`PredictRequest`][tserve.types.models.PredictRequest]: `past` or `fh` missing, `fh` not `> 0`, a table that is neither table shape, columns of unequal length, a row narrower than `columns` |
| **400** | the body was accepted but the request failed: the `model` is not loaded, `past` or `future` lacks the selected columns, target inference left nothing to forecast, or the estimator itself raised |
| **405** | wrong method, such as `GET /predict` (the body says to use `POST /predict`) |

The split is where the failure happens. **422** is FastAPI rejecting the JSON body before the handler runs, so the body is the usual FastAPI list of field errors. **400** is the handler wrapping everything after that:

```json
{
  "detail": {
    "error": "model 'chronos_2' is not loaded on this server (loaded: 'chronos_bolt', 'ttm_r3')",
    "code": "request_failed",
    "request_id": "…"
  }
}
```

A model that is missing from `GET /models` is 400, not 404. Missing columns read `past is missing columns: ['sales'] (available: ['timestamp', 'value'])`.

Estimator failures are wrapped rather than passed through, because the library wording for the same mistake ranges from clear to unrecognizable — Chronos Bolt past 64 steps raises `'ChronosBoltPipeline' object has no attribute 'quantiles'`. The message names the step that failed and the request values it failed on, quotes the estimator under `Original error:`, and points at the [catalog](../models/index.md):

| the step that failed | 400 opens with |
| --- | --- |
| the point forecast (`fit` then `predict`) | `Model 'chronos_bolt' failed to forecast 70 step(s) ahead from the 200 row(s) in past.` |
| the quantiles | `Model 'timesfm_2_5' returned its point forecast but failed on the requested quantiles [0.1, 0.9].` |

It does not try to diagnose the cause beyond that, so read the original error and compare the request against the context, horizon, and quantile support the catalog records for the model. An `fh` past the model's trained horizon and a `past` shorter than its context length both surface as the first one.

Asking a model that cannot produce quantiles for them is the one case TServe does decide: it is rejected before the estimator runs, so it reads `Model 'chronos_bolt' cannot return quantile predictions, so the requested quantiles [0.1, 0.9] are unavailable.` with no `Original error:` at all.

`POST /predict/bytes` behaves the same way, with 422 reserved for a missing `metadata` field or `past` file.

A **404** with `{"detail": "Not Found"}` is not a predict error: that path does not exist on this process. Check the URL, the port, and that you are posting to `/predict` — there is no version prefix.

## Python client

| raised | when |
| --- | --- |
| `ValidationError` | local, before any HTTP call: unsupported table shape, `fh` not `> 0`, missing time or target column |
| `RuntimeError` | the server answered 400 or higher; the message is `detail["error"]` when present, else the raw body |
| `httpx.RequestError` | connection refused, DNS failure, or timeout (default 60 s, set `timeout=` on `Client`) |
| `ValueError` | empty inferred target (time-only `past`, `future` holding the value column, or time only on a pandas index); or the response envelope is truncated, has wrong magic bytes, or an unsupported version |

`RuntimeError` is deliberately flat: the server-side type is gone by then, so read the message. Local `ValidationError`s never reach the network, which is why a wrong table shape fails instantly while an unloaded model needs a round trip.

The one surprising local failure is a pandas frame whose time axis is only the index. `time` then resolves to the first real column, target inference finds nothing left, and `coerce_request` raises `ValueError` before the request is sent. Call `reset_index()` first — see [Use an indexed pandas frame](../client/python.md#use-an-indexed-pandas-frame).

## Startup

These stop [`Server`][tserve.server.serve.Server] construction, which means the CLI exits before uvicorn binds the port:

| exception | when |
| --- | --- |
| `ValueError` | unknown model (the message lists the known models; a string that looks like a craft spec also hints to pass `(id, spec)` in Python or `id=spec` on the CLI), an empty craft spec or empty `id=` token, a duplicate model, or a path that is not a `.zip` |
| `TypeError` | an `(id, object)` pair whose object is neither a craft spec string nor a sktime `BaseForecaster`; or a craft spec that does not produce a `BaseForecaster` instance (for example a class name without parentheses) |
| `ImportError` | the executor's extra is not installed |
| `OSError` | `models_dir` does not exist or cannot be listed |
| `RuntimeError` | the model loaded but failed its warmup forecast, so it would fail on every request |

Whatever an estimator raises while loading propagates unchanged, so a failed Hugging Face download stops startup with that library's error. A [family extra](../models/index.md#dependencies) or image tag that matches the models you load is what avoids this. Loading a spec: [Craft specs](../server/craft-specs.md).
