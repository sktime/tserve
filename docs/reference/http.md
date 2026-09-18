# HTTP API

Routes served by the running [`Server`][fomo.server.serve.Server]. The process
publishes its own interactive copy of this page at
[/docs](http://127.0.0.1:8000/docs) and the raw schema at
[/openapi.json](http://127.0.0.1:8000/openapi.json). For worked requests, see
[HTTP](../client/http.md).

| method | path | response |
| --- | --- | --- |
| `POST` | `/predict` | [`PredictResponse`][fomo.types.models.PredictResponse] as JSON |
| `POST` | `/predict/bytes` | [`FOMO` envelope](#post-predictbytes) |
| `GET` | `/health` | [`HealthResult`][fomo.types.models.HealthResult] |
| `GET` | `/models` | [`ModelsResult`][fomo.types.models.ModelsResult] |
| `GET` | `/stats` | [`StatsResult`][fomo.types.models.StatsResult] |
| `GET` | `/` | [dashboard](../server/dashboard.md) HTML |
| `GET` | `/docs`, `/redoc`, `/openapi.json` | OpenAPI |

Prediction is POST only, so `GET /predict` is **405**. There is no path
prefix, no versioning, and no authentication: the origin is the process you
started. `/`, `/favicon.ico`, and the dashboard assets under `/static` are
excluded from the OpenAPI schema.

## POST /predict

`Content-Type: application/json`. The body is
[`PredictRequest`][fomo.types.models.PredictRequest] — `past` and `fh` are
required, `model` defaults to `naive`. Field meanings,
table shapes, and inference rules are in the
[data specification](../client/data.md).

The response is column-oriented JSON: `predictions`, `quantiles` (`null`
unless requested and supported), `model`, and a server-assigned `request_id`.

| status | meaning |
| --- | --- |
| 200 | prediction produced |
| 400 | body was valid but the request failed (unloaded id, missing column, estimator error) |
| 422 | body does not match `PredictRequest` |

Bodies for both failures are in [Errors](errors.md#predict-requests).

## POST /predict/bytes

The Arrow route used by [`Client`][fomo.client.client.Client]. It exists so
tables cross the wire as Arrow IPC instead of JSON numbers; the fields are the
same as `POST /predict`.

The request is `multipart/form-data`:

| part | kind | contents |
| --- | --- | --- |
| `metadata` | form field | JSON object of the non-table fields (`time`, `target`, `fh`, `model`, `quantiles`) |
| `past` | file | Arrow IPC stream, `application/vnd.apache.arrow.stream` |
| `future`, `static` | file | optional Arrow IPC streams; empty bodies are ignored |

The response media type is `application/vnd.fomo.predict+arrow`, an envelope
of length-prefixed parts:

```text
b"FOMO"     magic, 4 bytes
0x01        version, 1 byte
uint32      number of parts        (little-endian, as are all lengths)
per part:
  uint32    length of the part name
  bytes     part name
  uint32    length of the payload
  bytes     payload
```

The part named `response` is JSON metadata (`model`, `request_id`). The
remaining parts are Arrow IPC streams: `predictions`, plus `quantiles` when
requested. Missing `metadata` or `past` parts are **422**; anything failing
after that — unparsable metadata, an unreadable Arrow stream, a failed
prediction — is **400** with the same body as the JSON route.

## Status routes

`GET /health` reports process liveness, not whether models are warm. It
currently always returns `{"status": "ok"}`; the `error` field in the schema
is unused.

`GET /models` lists what this process loaded, not the registry
[catalog](../models/index.md):

```json
{
  "models": [
    {"id": "naive", "executor": "sktime", "source": "registry"},
    {"id": "chronos-bolt", "executor": "sktime", "source": "registry"}
  ]
}
```

`source` is `registry`, `directory` (a saved `.zip`), `object` (a live
estimator), or `craft` (a sktime craft spec). How to load a spec:
[Craft specs](../server/craft-specs.md). `executor` is the plugin that
loaded it, today always `sktime`.

`GET /stats` is a snapshot of the process:

```json
{
  "uptime_s": 3600.5,
  "memory": {"cpu_rss_mb": 512.25, "gpu_mb": 1024.0},
  "models": {
    "chronos-bolt": {
      "executor": "sktime",
      "load_s": 1.24,
      "warmup_s": 0.31,
      "requests": {"total": 12, "ok": 11, "failed": 1},
      "latency_s": {
        "count": 12,
        "total": 1.86,
        "mean": 0.155,
        "fastest": 0.041,
        "slowest": 0.38
      }
    }
  }
}
```

Keys under `models` are loaded model ids. Timings are wall-clock seconds, and
failed predicts count in both `requests.failed` and `latency_s`. Either memory
probe is `null` when it is unavailable — `gpu_mb` needs torch already imported
with CUDA present. Field-by-field types are in
[`StatsResult`][fomo.types.models.StatsResult].
