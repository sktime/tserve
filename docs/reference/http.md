# HTTP API

Routes live on [`fomo.server.routes`][fomo.server.routes] and are included by [`Server`][fomo.server.serve.Server]. After `fomo serve`, the live OpenAPI UI is the interactive source of truth:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

There is no hosted FoMo API. Those URLs stay on the running app.

| method | path | |
| --- | --- | --- |
| `GET` | `/` | browser dashboard (JSON endpoints only; not `/forecast/bytes`) |
| `GET` | `/health` | liveness; currently always [`HealthResult`][fomo.types.models.HealthResult] `status="ok"` |
| `GET` | `/models` | loaded models ([`ModelsResult`][fomo.types.models.ModelsResult]) |
| `GET` | `/stats` | uptime, memory, per loaded-id metrics ([`StatsResult`][fomo.types.models.StatsResult]) |
| `POST` | `/forecast` | JSON [`ForecastRequest`][fomo.types.models.ForecastRequest] |
| `POST` | `/forecast/bytes` | multipart metadata + Arrow frames; response `application/vnd.fomo.forecast+arrow` |
| `GET` | `/docs` | FastAPI Swagger UI |
| `GET` | `/redoc` | FastAPI ReDoc |
| `GET` | `/openapi.json` | OpenAPI schema |

`GET /health` is liveness, not “models are warm”. [`HealthError`][fomo.types.models.HealthError] is a nested payload on `HealthResult.error`, not something the handler raises; the live route omits `error`.

## JSON `POST /forecast`

`Content-Type: application/json`. Body is [`ForecastRequest`][fomo.types.models.ForecastRequest]. The handler assigns a UUID `request_id`, runs [`coerce_request`][fomo.types.converters.coerce_request], then [`Scheduler.run`][fomo.scheduling.scheduler.Scheduler.run]. On success, [`ForecastResponse`][fomo.types.models.ForecastResponse] with `predictions` / `quantiles` as column dicts.

Invalid JSON bodies that fail Pydantic validation are **422** before the handler runs. Coerce or predict failures are **400** with `detail` `{error, code: "request_failed", request_id}`. See [Errors](errors.md).

`request.model` is a loaded model id. Tables: [Forecast tables](../concepts/forecast-tables.md).

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "past": {
      "timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],
      "sales": [120, 135, 128, 142, 138]
    },
    "time": "timestamp",
    "target": ["sales"],
    "fh": 3,
    "model": "naive"
  }'
```

## Bytes `POST /forecast/bytes`

This is the [`Client`][fomo.client.client.Client] / [`HttpTransport`][fomo.client.transports.http.HttpTransport] wire. Form field `metadata` is a JSON string of scalar fields (`time`, `target`, `fh`, `model`, `quantiles`, …). File `past` is required; `future` and `static` are optional. Empty file bodies for `future` / `static` are skipped. Arrow parts use content type `application/vnd.apache.arrow.stream`.

The handler [`decode_request`][fomo.types.converters.decode_request], runs the scheduler, overwrites `request_id` (sktime [`to_response`][fomo.runtime.executors.sktime.converters.to_response] leaves `""`), then [`encode_response`][fomo.types.converters.encode_response] and [`pack_envelope`][fomo.types.converters.pack_envelope]. Media type is `application/vnd.fomo.forecast+arrow`. Failures use the same HTTP 400 wrapping as JSON.

## Status

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}

curl -s http://127.0.0.1:8000/models
# {"models":[{"id":"naive","executor":"sktime","source":"registry"}]}

curl -s http://127.0.0.1:8000/stats
```

[`Stats.snapshot`][fomo.logging.stats.Stats.snapshot] is validated as [`StatsResult`][fomo.types.models.StatsResult]: `uptime_s`, `memory` (`cpu_rss_mb`, `gpu_mb`; either may be `None`), and per **loaded model id** load/warmup/request/latency counters.
