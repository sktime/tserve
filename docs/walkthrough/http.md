# HTTP

JSON `POST /forecast` is the language-agnostic path. The [Python client](python.md) does **not** post JSON; it posts Arrow to `/forecast/bytes`. The request fields are the same either way.

The server must already be running with the `model` id loaded. See [Server](server.md).

| method | path | |
| --- | --- | --- |
| `GET` | `/` | [dashboard](dashboard.md) |
| `GET` | `/health` | liveness, not “models are warm” |
| `GET` | `/models` | loaded ids + executor + source |
| `GET` | `/stats` | uptime, RSS, per-model load/warmup/latency |
| `POST` | `/forecast` | JSON |
| `POST` | `/forecast/bytes` | Arrow (`Client`) |
| `GET` | `/docs` | Swagger |
| `GET` | `/redoc` | ReDoc |
| `GET` | `/openapi.json` | OpenAPI schema |

`GET /forecast` is **405 Method Not Allowed**. The body must be a POST.

Live UIs: dashboard `/`, Swagger `/docs`, ReDoc `/redoc`.

## `GET /health`

Liveness of the process, not “models are warm”.

```bash
curl -s http://127.0.0.1:8000/health
```

```json
{"status":"ok"}
```

## `GET /models`

Loaded ids only — not the [registry catalog](models.md).

```bash
curl -s http://127.0.0.1:8000/models
```

```json
{"models":[{"id":"naive","executor":"sktime","source":"registry"},{"id":"chronos-bolt-tiny","executor":"sktime","source":"registry"},{"id":"ttm-r3-512-30","executor":"sktime","source":"registry"}]}
```

## `GET /stats`

Uptime, memory probes, and per loaded-id load / warmup / latency.

```bash
curl -s http://127.0.0.1:8000/stats
```

## `GET /`

Browser [dashboard](dashboard.md) (`text/html`). Static assets under `/static`.

```bash
curl -s -D - -o /dev/null http://127.0.0.1:8000/
```

## `POST /forecast`

JSON body. See [request fields](#request-fields) and [data format](#data-format).

```bash
curl -s http://127.0.0.1:8000/forecast -H 'Content-Type: application/json' -d '{"past": {"timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"], "sales": [120, 135, 128, 142, 138]}, "time": "timestamp", "target": ["sales"], "fh": 3, "model": "chronos-bolt-tiny"}'
```

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [139.96, 138.93, 138.26]
  },
  "quantiles": null,
  "model": "chronos-bolt-tiny",
  "request_id": "…"
}
```

Swap `model` to any other loaded id (`ttm-r3-512-30`, `naive`, …).

## `POST /forecast/bytes`

Arrow IPC inside a `FOMO` envelope (`application/vnd.fomo.forecast+arrow`). This is what [`Client`][fomo.client.client.Client] sends. You normally do not build the multipart body by hand.

## OpenAPI

| method | path | |
| --- | --- | --- |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |
| `GET` | `/openapi.json` | OpenAPI schema |

```bash
curl -s http://127.0.0.1:8000/openapi.json | head
```

JSON validation failures are HTTP 422. Coerce or predict failures are HTTP 400 with `{ "detail": { "error", "code": "request_failed", "request_id" } }`. See [Errors](../reference/errors.md).

## Request fields

Long tables plus roles, not a 1-d `y` vector. Same fields on JSON and `Client.forecast(...)`.

| field | |
| --- | --- |
| `past` | **required.** Historical observations as a table: one row per timestamp. Must include a time column and at least one numeric target column. This is not a Series and not “just the y values”. |
| `fh` | **required.** Steps ahead (`> 0`) |
| `time` | optional. Name of the timestamp column in `past`. Omitted → first column of `past` |
| `target` | optional. Target column name(s). A string becomes a one-element list. Omitted → remaining `past` columns |
| `model` | optional. Default `"naive"`; must already be loaded (`GET /models`) |
| `future` | optional. Future timestamps (and extra columns; see [covariates](python.md#covariates)) |
| `static` | optional. One row of static features, broadcast over time |
| `quantiles` | optional. e.g. `[0.1, 0.5, 0.9]`; the estimator must implement `predict_quantiles` |

Panel (`series_id`) and hierarchical frames are not supported. Time must be a column — if your pandas object uses a `DatetimeIndex`, call `reset_index()` first. See [Python](python.md#sktime-and-indexed-frames).

## Data format

`past`, `future`, `static`, `predictions`, and `quantiles` accept any of these shapes. JSON typically uses a column dict or a row matrix.

**Column dict** (name → list of equal length) — used in the [POST](#post-forecast) example above.

**Row matrix:**

```json
{
  "past": {
    "columns": ["timestamp", "sales"],
    "data": [
      ["2024-01-01", 120],
      ["2024-01-02", 135],
      ["2024-01-03", 128],
      ["2024-01-04", 142],
      ["2024-01-05", 138]
    ]
  },
  "time": "timestamp",
  "target": ["sales"],
  "fh": 3,
  "model": "chronos-bolt-tiny"
}
```

You can omit `time` and `target` when the first column is time and the rest are targets.

## Univariate forecast

One target column. The curl example under [POST /forecast](#post-forecast) is the whole contract.

`target` can be a list of several columns if the loaded estimator accepts multivariate `y`. Extra columns on `past` that are not `time` or `target` are ignored unless you omit `target` (then they become targets).

## Errors you will hit

| status | meaning |
| --- | --- |
| **405** | `GET /forecast` — use POST |
| **422** | body failed [`ForecastRequest`][fomo.types.models.ForecastRequest] (missing `past` / `fh`, `fh <= 0`, bad table shape) |
| **400** | coerce or predict failed (id not loaded, missing columns, estimator error) |

A 400 for an unknown id looks like:

```json
{
  "detail": {
    "error": "model 'timesfm-2.5' is not loaded on this server (loaded: 'chronos-bolt-tiny', 'naive', 'ttm-r3-512-30')",
    "code": "request_failed",
    "request_id": "…"
  }
}
```
