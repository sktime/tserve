# Overview

![FoMo architecture](assets/architecture.svg)

Walk top to bottom. Three seams:

- **Transports** do not import each other. JSON (`POST /forecast`) coerces on the server. The Python [`Client`][fomo.client.client.Client] coerces locally and sends Arrow (`POST /forecast/bytes`). A third lane is a new transport class, not a runtime change.
- **Canonical frames** are `CoercedForecastRequest` / `CoercedForecastResponse` — Narwhals `DataFrame`. Callers pass a dict, pandas, polars, or pyarrow; they get the same type back.
- **Executors** own convert → execute → convert back. The sktime executor maps Narwhals onto `y, X, fh`. Executors do not share converters.

## What you run

[`Server`][fomo.server.serve.Server] (or `fomo serve`) loads the models you name, then serves:

| you want | where |
| --- | --- |
| Browser console | [Dashboard](walkthrough/dashboard.md) at `GET /` |
| JSON forecasts | `POST /forecast` — [Client](walkthrough/client.md) |
| Python forecasts | [`Client`][fomo.client.client.Client] |
| Live OpenAPI | `/docs`, `/redoc` |
| Loaded ids | `GET /models` |

The [registry](walkthrough/models.md) is the list of ids the process *can* load. `--load-models` is the list it *did* load. Forecast `model` must be a loaded id.

## Request shape

A forecast is tables plus column roles, not a 1-d `y` vector. The same fields go on JSON and `Client.forecast(...)`:

| field | |
| --- | --- |
| `past` | required. one row per timestamp |
| `fh` | required. steps ahead (`> 0`) |
| `time`, `target` | optional. omitted → first column of `past`, remaining columns as targets |
| `model` | optional. default `"naive"` — still must be loaded |
| `future`, `static` | optional covariate tables |
| `quantiles` | optional, e.g. `[0.1, 0.5, 0.9]` |

JSON tables are **column dicts**: `{"col": [values...]}`. A row matrix `{"columns": [...], "data": [[...], ...]}` is also accepted.

Panel (multi-series) input is not supported.

## Next

1. [Start a server](walkthrough/server.md)
2. [Load models](walkthrough/models.md)
3. [Send forecasts](walkthrough/client.md)
