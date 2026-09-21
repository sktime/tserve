# Overview

![TServe architecture](assets/architecture.svg)

Walk top to bottom. Three seams:

- **Transports** do not import each other. JSON (`POST /predict`) coerces on the server. The Python [`Client`][tserve.client.client.Client] coerces locally and sends Arrow (`POST /predict/bytes`). A third lane is a new transport class, not a runtime change.
- **Canonical frames** are `CoercedPredictRequest` / `CoercedPredictResponse` — Narwhals `DataFrame`. Callers pass a dict, pandas, polars, or pyarrow; they get the same type back.
- **Executors** own convert → execute → convert back. The sktime executor maps Narwhals onto `y, X, fh`. Executors do not share converters. A `pytorch-forecasting` plugin slot exists in the tree but is not implemented.

## What you run

[`Server`][tserve.server.serve.Server] (or `tserve`) loads selected models, then serves:

| you want | where |
| --- | --- |
| Browser console | [Dashboard](server/dashboard.md) at `GET /` |
| JSON predictions | `POST /predict` — [HTTP](client/http.md) |
| Python predictions | [`Client`][tserve.client.client.Client] — [Python](client/python.md) |
| Live OpenAPI | `/docs`, `/redoc` |
| Loaded models | `GET /models` |

The [catalog](models/index.md) is the list of models the process *can* load. Leftover CLI positionals name extra models on top of `naive`, a test baseline. Predict `model` must be a loaded model.

Install extras to match what you will load. `server` includes `sktime` (enough for [`naive`](models/base.md)). Hub families are separate extras ([`hub`](models/hub.md), [`chronos`](models/chronos.md), [`granite`](models/granite.md), …) and matching [Docker tags](server/docker.md). See [Dependencies](models/index.md#dependencies); each extra also has its own page under [Models](models/index.md).

## Request shape

A prediction request is tables plus column roles, not a 1-d `y` vector. The same fields go on JSON and `Client.predict(...)`:

| field | |
| --- | --- |
| `past` | required. historical table: one row per timestamp, with a time column and target values |
| `fh` | required. steps ahead (`> 0`) |
| `time`, `target` | optional. omitted → first `past` column as time; remaining columns not present in `future` as targets |
| `model` | optional. default `"naive"` |
| `future` | optional future timestamps |
| `static` | optional one-row static values |
| `quantiles` | optional, e.g. `[0.1, 0.5, 0.9]` |

Tables may be a column dict, a `{columns, data}` row matrix, pandas, polars, pyarrow, or Narwhals — see the [data specification](client/data.md). Time must be a **column**. A pandas `DatetimeIndex` or an sktime Series is not enough; call `reset_index()` first.

Panel (multi-series) and hierarchical input are not supported.

## Next

1. [Start a server](server/index.md) (extras and tags: [Dependencies](models/index.md#dependencies))
2. [Catalog](models/index.md)
3. [Send predictions](client/index.md) over HTTP or from Python
