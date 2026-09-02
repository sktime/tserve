# Client

Same package as the server. JSON over HTTP for any language; [`Client`][fomo.client.client.Client] if you already have a dataframe (Arrow on the wire, your type back).

The server must already be running with the `model` id loaded. See [Server](server.md).

## HTTP

Liveness:

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}
```

Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

JSON `POST /forecast` is the curl path. The Python client does **not** post JSON; it posts Arrow to `/forecast/bytes`. Same request fields either way.

## Python client

Already in the env if you installed extras for the server. On a machine that only calls a remote server:

```bash
pip install 'fomo[client]'
```

From a clone:

```bash
uv sync --extra client
```

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    client.health()
    # status='ok'
    client.models()
```

`Client.models()` lists loaded ids only.

## Request fields

Long tables plus roles, not a 1-d `y` vector. Same fields on JSON and `Client.forecast(...)`.

| field | |
| --- | --- |
| `past` | required. one row per timestamp |
| `fh` | required. steps ahead (`> 0`) |
| `time` | optional. timestamp column; omitted → first column of `past` |
| `target` | optional. always becomes a list; omitted → remaining `past` columns |
| `model` | optional. default `"naive"`; must be loaded |
| `future` | optional. future timestamps (and unused extra columns) |
| `static` | optional. one row of static features, broadcast over time |
| `quantiles` | optional. e.g. `[0.1, 0.5, 0.9]`; estimator must support it |

JSON tables are **column dicts**: `{"col": [values...]}`. A row matrix `{"columns": [...], "data": [[...], ...]}` is also accepted.

pandas, polars, pyarrow, and Narwhals frames work on the Python client.

Panel (`series_id`) is not supported.

## Univariate forecast

curl (JSON):

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

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [138.0, 138.0, 138.0]
  },
  "quantiles": null,
  "model": "naive",
  "request_id": "…"
}
```

Same kwargs on the client (dict in → dict out):

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past={
            "timestamp": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "sales": [120, 135, 128, 142, 138],
        },
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
    )

print(result.predictions)
# {'timestamp': [...], 'sales': [138.0, 138.0, 138.0]}
```

`naive` is a drift `NaiveForecaster` — that is the pipe. Swap `model` to `chronos-2` / `timesfm-2.5` on a server that loaded those ids.

You can omit `time` and `target` when the first column is time and the rest are targets:

```python
result = client.forecast(past=past, fh=3, model="naive")
```

## Covariates

`static` is one row, broadcast over time as exogenous `X`. `future` is optional; when `static` is set it supplies the future **index** (must include `time`). Extra columns on `future` are not mapped onto sktime `X` today.

```python
import pandas as pd

past = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "sales": [120, 135, 128, 142, 138],
    }
)
static = pd.DataFrame({"store_type": ["urban"]})
future = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-06", periods=3, freq="D"),
    }
)

result = client.forecast(
    past=past,
    future=future,
    static=static,
    time="timestamp",
    target=["sales"],
    fh=3,
    model="naive",
)
print(result.predictions)
```

## Quantiles

Add `quantiles=[0.1, 0.5, 0.9]`. Columns come back flattened: `{variable}_{alpha}` (often positional `0`, e.g. `0_0.1`). The estimator must implement `predict_quantiles`; otherwise the request fails.

```python
result = client.forecast(
    past=past,
    time="timestamp",
    target=["sales"],
    fh=3,
    quantiles=[0.1, 0.5, 0.9],
    model="naive",
)
print(result.predictions)
print(result.quantiles)
```

`predictions` stays the point forecast. `quantiles` is a second table, or `null` / `None` when the field was omitted.

On a Hub model that supports quantiles (`timesfm-2.5`, `flowstate`, …):

```bash
uv run fomo serve --load-models timesfm-2.5
```

then the same call with `model="timesfm-2.5"`.

## Frame in, frame out

Whatever you pass as `past` is what `predictions` / `quantiles` come back as.

```python
import pandas as pd
from fomo.client import Client

past = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "sales": [120, 135, 128, 142, 138],
    }
)

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
    )

type(result.predictions)  # pandas.DataFrame
```

Polars in → polars out. No extra convert on your side.

Default timeout is 60s. Hub models can need longer:

```python
Client("http://127.0.0.1:8000", timeout=120.0)
```

## Other endpoints

| method | path | |
| --- | --- | --- |
| `GET` | `/health` | liveness, not “models are warm” |
| `GET` | `/models` | loaded ids + executor + source |
| `GET` | `/stats` | uptime, RSS, per-model load/warmup/latency |
| `POST` | `/forecast` | JSON |
| `POST` | `/forecast/bytes` | Arrow (`Client`) |
| `GET` | `/docs` | Swagger |
| `GET` | `/redoc` | ReDoc |

`client.health()` / `.models()` / `.stats()` wrap the three GETs.

JSON validation failures are HTTP 422. Coerce or predict failures are HTTP 400 with `{ "detail": { "error", "code": "request_failed", "request_id" } }`. The client raises `RuntimeError` with the `error` message. See [Errors](../reference/errors.md).
