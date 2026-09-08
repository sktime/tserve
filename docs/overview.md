# Overview

![FoMo architecture](assets/architecture.svg)

Walk top to bottom. Three seams:

- **Transports** do not import each other. JSON (`POST /forecast`) coerces on the server. The Python [`Client`][fomo.client.client.Client] coerces locally and sends Arrow (`POST /forecast/bytes`). A third lane is a new transport class, not a runtime change.
- **Canonical frames** are `CoercedForecastRequest` / `CoercedForecastResponse` — Narwhals `DataFrame`. Callers pass a dict, pandas, polars, or pyarrow; they get the same type back.
- **Executors** own convert → execute → convert back. The sktime executor maps Narwhals onto `y, X, fh`. Executors do not share converters. A `pytorch-forecasting` plugin slot exists in the tree but is not implemented.

## What you run

[`Server`][fomo.server.serve.Server] (or `fomo serve`) loads the models you name, then serves:

| you want | where |
| --- | --- |
| Browser console | [Dashboard](server/dashboard.md) at `GET /` |
| JSON forecasts | `POST /forecast` — [HTTP](client/http.md) |
| Python forecasts | [`Client`][fomo.client.client.Client] — [Python](client/python.md) |
| Live OpenAPI | `/docs`, `/redoc` |
| Loaded ids | `GET /models` |

The [catalog](models/catalog.md) is the list of ids the process *can* load. `--load-models` is the list it *did* load. Forecast `model` must be a loaded id. See [Load models](models/index.md).

Install extras to match what you will load. `server` includes `sktime` (enough for `naive`). Hub families are separate extras (`hub`, `chronos`, `granite`, …) and matching [Docker tags](server/docker.md).

## Request shape

A forecast is tables plus column roles, not a 1-d `y` vector. The same fields go on JSON and `Client.forecast(...)`:

| field | |
| --- | --- |
| `past` | required. historical table: one row per timestamp, with a time column and target values |
| `fh` | required. steps ahead (`> 0`) |
| `time`, `target` | optional. omitted → first column of `past`, remaining columns as targets |
| `model` | optional. default `"naive"` — still must be loaded |
| `future`, `static` | optional covariate tables |
| `quantiles` | optional, e.g. `[0.1, 0.5, 0.9]` |

Tables may be a column dict, a `{columns, data}` row matrix, pandas, polars, pyarrow, or Narwhals — see [data format](client/http.md#data-format). Time must be a **column**. A pandas `DatetimeIndex` or an sktime Series is not enough; call `reset_index()` first.

Panel (multi-series) and hierarchical input are not supported.

## Next

1. [Start a server](server/index.md) (including [dependencies](server/index.md#dependencies))
2. [Load models](models/index.md)
3. [Send forecasts](client/http.md) over HTTP or from [Python](client/python.md)
