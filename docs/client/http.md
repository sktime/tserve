# HTTP

Send JSON to `POST /predict` from any language. The request fields are the same as [`Client.predict(...)`](python.md), but the Python client uses Arrow instead of this JSON route.

## Endpoints

| method | path | what it gives you |
| --- | --- | --- |
| `POST` | `/predict` | [JSON prediction](#send-a-prediction) |
| `POST` | `/predict/bytes` | [Arrow prediction](#arrow-endpoint), used by the Python client |
| `GET` | `/health` | [process liveness](#inspect-the-server) |
| `GET` | `/models` | [loaded models](#inspect-the-server) |
| `GET` | `/stats` | [uptime, memory, per-model metrics](#inspect-the-server) |
| `GET` | `/` | browser [dashboard](../server/dashboard.md) |
| `GET` | `/docs`, `/redoc`, `/openapi.json` | live OpenAPI |

Every route returns JSON except `/predict/bytes`, which speaks Arrow, and `/`, which serves the dashboard. The [HTTP API reference](../reference/http.md) lists the same routes with schema links.

## Start a server

The point forecast examples use `chronos_bolt`. Quantile examples use `timesfm_2_5`, whose estimator supports quantile prediction; Chronos Bolt does not:

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt timesfm_2_5
```

See [Server](../server/index.md) for Docker, uv / pip, and server options. The URLs below belong to this local process; TServe does not provide a hosted API.

## Send a prediction

`past` is a table, not a 1-d vector. This example sends five days of sales and asks for the next three:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "chronos_bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
    ```

`POST /predict` returns a column-oriented JSON table:

```json
{
  "predictions": {
    "timestamp": [
      "2024-01-06T00:00:00",
      "2024-01-07T00:00:00",
      "2024-01-08T00:00:00"
    ],
    "sales": [139.96, 138.93, 138.26]
  },
  "quantiles": null,
  "model": "chronos_bolt",
  "request_id": "…"
}
```

See [Data specification](data.md) for every request and response field.

## Use row-oriented JSON

Tables can also use `columns` and `data`. Here `time` and `target` are omitted, so TServe uses the first column as time and the other column as the target:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
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
      "fh": 3,
      "model": "chronos_bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"columns":["timestamp","sales"],"data":[["2024-01-01",120],["2024-01-02",135],["2024-01-03",128],["2024-01-04",142],["2024-01-05",138]]},"fh":3,"model":"chronos_bolt"}'
    ```

The response is still column-oriented JSON. HTTP does not preserve the row-oriented request shape.

## Request quantiles

Quantiles are a second result table. The estimator must support quantile prediction, so this example uses the loaded `timesfm_2_5` model:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01"],
        "sales": [120, 135, 128, 142, 150]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "timesfm_2_5",
      "quantiles": [0.1, 0.5, 0.9]
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-02-01","2024-03-01","2024-04-01","2024-05-01"],"sales":[120,135,128,142,150]},"time":"timestamp","target":["sales"],"fh":3,"model":"timesfm_2_5","quantiles":[0.1,0.5,0.9]}'
    ```

Many estimators name those columns `{target}_{level}` (`sales_0.1`, `sales_0.5`, `sales_0.9`). `timesfm_2_5` currently uses a positional prefix (`0_0.1`, `0_0.5`, `0_0.9`). See [Quantiles](data.md#quantiles) for the response shape and model limitation.

## Inspect the server

Use the JSON status routes to check the process and its loaded models:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/health
    curl -s http://127.0.0.1:8000/models
    curl -s http://127.0.0.1:8000/stats
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/health
    curl.exe -s http://127.0.0.1:8000/models
    curl.exe -s http://127.0.0.1:8000/stats
    ```

`GET /health` checks process liveness, not whether models are warm. `GET /models` lists loaded models, not the registry [catalog](../models/index.md).

Point a browser at `/` for the [dashboard](../server/dashboard.md) or `/docs` to try the endpoints from Swagger.

## Arrow endpoint

`POST /predict/bytes` accepts multipart metadata and Arrow IPC tables and returns a `TServe` envelope with media type `application/vnd.tserve.predict+arrow`. This is the route used by the [Python client](python.md); you normally do not construct its body yourself.

## Errors

Prediction is POST-only. `GET /predict` returns **405 Method Not Allowed**. Invalid JSON request shapes return **422**. Coercion and prediction failures, including an unloaded model, return **400** with an error message and `request_id`.

See [Errors](../reference/errors.md) for response bodies and Python exceptions.
