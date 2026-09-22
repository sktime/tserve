# Overview

TServe is a process you run. It loads named models once, keeps them warm, and answers forecast requests. There is no hosted API.

![TServe architecture](assets/architecture.svg)

| you want | where |
| --- | --- |
| Browser console | [Dashboard](server/dashboard.md) at `GET /` |
| JSON predictions | `POST /predict` — [HTTP](client/http.md) |
| Python predictions | [`Client`][tserve.client.client.Client] — [Python](client/python.md) |
| Live OpenAPI | `/docs`, `/redoc` |
| Loaded models | `GET /models` |

JSON and Python send the same fields. JSON is coerced on the server. The Python client coerces locally and posts Arrow to `POST /predict/bytes`.

## What gets loaded

The [catalog](models/index.md) is what a process *can* load. You name the models to load. `naive` always loads, so you can test the process without a download. `GET /models` lists what this process loaded.

Install the extra, or pull the Docker tag, that matches the family. [`server`](models/base.md) is enough for `naive`. Hub families are separate extras and tags: [Dependencies](models/index.md#dependencies).

## Request

A prediction is tables plus column roles. The same fields go on JSON and `Client.predict(...)`:

| field | |
| --- | --- |
| `past` | required. one row per timestamp, with a time column and the targets |
| `fh` | required. steps ahead (`> 0`) |
| `time`, `target` | optional. omitted: first column is time; other columns not in `future` are targets |
| `model` | optional. default `"naive"`, and it must be loaded |
| `future` | optional. known future values of covariates |
| `static` | optional. one row of values that stay constant |
| `quantiles` | optional, e.g. `[0.1, 0.5, 0.9]` |

```json
{
  "past": {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    "sales": [120, 135, 128, 142, 138]
  },
  "fh": 3,
  "model": "chronos_bolt"
}
```

Time is a column. Call `reset_index()` before sending a pandas `DatetimeIndex` or an sktime Series. Panel and hierarchical input are not supported. Every format and rule: [data specification](client/data.md).

## Next

1. [Install](installation.md)
2. [Quick start](quick-start.md)
3. [Choose a model](models/index.md)
4. [Send a prediction](client/index.md)
