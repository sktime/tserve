# Quickstart

Start a local process, open the live OpenAPI UI, then send the same univariate forecast with curl and [`Client`][fomo.client.client.Client].

## 1. Start the server

```bash
uv pip install -e '.[server,sktime-lite,client]'
fomo serve --load-models naive
```

This binds [http://127.0.0.1:8000](http://127.0.0.1:8000) by default (`--host 127.0.0.1`, `--port 8000`). A bare `fomo serve` (no `--load-models`) loads nothing; forecasts against `naive` would then fail with HTTP 400.

Confirm what is loaded:

```bash
curl -s http://127.0.0.1:8000/models
# {"models":[{"id":"naive","executor":"sktime","source":"registry"}]}
```

## 2. Open live docs

In a browser:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

There is no hosted FoMo API. Every URL is the process you just started (or the `--host` / `--port` / Docker `-p` you set).

## 3. Forecast with curl

JSON tables may be a row matrix `{columns, data}` or a column dict (name → list). The OpenAPI example uses `{columns, data}`:

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
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
    "model": "naive"
  }'
```

Same payload as a column dict:

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

JSON `POST /forecast` returns [`ForecastResponse`][fomo.types.models.ForecastResponse] with `predictions` as a column dict (`DataFrame.to_dict(as_series=False)`):

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [138.0, 138.0, 138.0]
  },
  "quantiles": null,
  "model": "naive",
  "request_id": "..."
}
```

`past` and `fh` (`> 0`) are required. `time` may be omitted (first column of `past`). `target` may be omitted (inferred from `past` columns other than `time` and any `future` columns). `model` defaults to `"naive"` if omitted; spell it out so the request matches a loaded id.

The body is [`ForecastRequest`][fomo.types.models.ForecastRequest]. See [Forecast tables](../concepts/forecast-tables.md) for accepted shapes and [HTTP](../reference/http.md) for every route.

## 4. Same forecast with `Client`

[`Client.forecast`][fomo.client.client.Client.forecast] takes the same fields. It does **not** POST JSON `/forecast`; the default [`HttpTransport`][fomo.client.transports.http.HttpTransport] sends Arrow to `POST /forecast/bytes` and restores the native type of `past`.

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past={
            "columns": ["timestamp", "sales"],
            "data": [
                ["2024-01-01", 120],
                ["2024-01-02", 135],
                ["2024-01-03", 128],
                ["2024-01-04", 142],
                ["2024-01-05", 138],
            ],
        },
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
    )

print(result.predictions)
print(result.model, result.request_id)
```

`GET /models` lists loaded ids only. Next: [first forecast with pandas](../tutorials/first-forecast.md).
