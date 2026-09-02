# HTTP

Routes on the running [`Server`][fomo.server.serve.Server]. Live OpenAPI is the interactive source of truth: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

| method | path | |
| --- | --- | --- |
| `GET` | `/` | [dashboard](../walkthrough/dashboard.md) |
| `GET` | `/health` | liveness; currently always `{"status":"ok"}` |
| `GET` | `/models` | loaded models (`id`, `executor`, `source`) |
| `GET` | `/stats` | uptime, memory, per loaded-id metrics |
| `POST` | `/forecast` | JSON body — [`ForecastRequest`][fomo.types.models.ForecastRequest] |
| `POST` | `/forecast/bytes` | Arrow; used by [`Client`][fomo.client.client.Client] |
| `GET` | `/docs` | Swagger |
| `GET` | `/redoc` | ReDoc |
| `GET` | `/openapi.json` | OpenAPI schema |

`GET /health` is not “models are warm”. `GET /models` is not the registry catalog.

## JSON `POST /forecast`

`Content-Type: application/json`. Fields: [Client](../walkthrough/client.md#request-fields).

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
    "model": "flowstate"
  }'
```

Invalid bodies are **422**. Coerce or predict failures are **400** — see [Errors](errors.md).

## Bytes `POST /forecast/bytes`

Multipart: JSON `metadata` plus Arrow files (`past` required; `future` / `static` optional). Response media type `application/vnd.fomo.forecast+arrow`. You normally go through [`Client`][fomo.client.client.Client] instead of building this by hand.
