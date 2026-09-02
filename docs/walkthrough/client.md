# Client

Same package as the server. JSON over HTTP for any language; [`Client`][fomo.client.client.Client] if you already have a dataframe (Arrow on the wire, your table type back).

The server must already be running with the `model` id loaded. See [Server](server.md).

## HTTP

JSON `POST /forecast` is the curl path. The Python client does **not** post JSON; it posts Arrow to `/forecast/bytes`. Same request fields either way.

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

Live UIs: dashboard `/`, Swagger `/docs`, ReDoc `/redoc`.

### `GET /health`

Liveness of the process, not “models are warm”.

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}
```

### `GET /models`

Loaded ids only — not the [registry catalog](models.md).

```bash
curl -s http://127.0.0.1:8000/models
# {"models":[{"id":"naive","executor":"sktime","source":"registry"}, …]}
```

### `GET /stats`

Uptime, memory probes, and per loaded-id load / warmup / latency.

```bash
curl -s http://127.0.0.1:8000/stats
```

### `GET /`

Browser [dashboard](dashboard.md) (`text/html`). Static assets under `/static`.

```bash
curl -s -D - -o /dev/null http://127.0.0.1:8000/
# HTTP/1.1 200 OK
# content-type: text/html; charset=utf-8
```

### `POST /forecast`

JSON body. See [request fields](#request-fields) and [data format](#data-format).

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
    "model": "timesfm-2.5"
  }'
```

### `POST /forecast/bytes`

Arrow IPC inside a `FOMO` envelope (`application/vnd.fomo.forecast+arrow`). This is what [`Client`][fomo.client.client.Client] sends. You normally do not build the multipart body by hand.

### OpenAPI

| method | path | |
| --- | --- | --- |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |
| `GET` | `/openapi.json` | OpenAPI schema |

```bash
curl -s http://127.0.0.1:8000/openapi.json | head
```

`client.health()` / `.models()` / `.stats()` wrap the three JSON GETs. JSON validation failures are HTTP 422. Coerce or predict failures are HTTP 400 with `{ "detail": { "error", "code": "request_failed", "request_id" } }`. The client raises `RuntimeError` with the `error` message. See [Errors](../reference/errors.md).

## Python client

Already in the env if you `uv sync --all-extras` for the server. On a machine that only calls a remote server, from a clone:

```bash
uv sync --extra client
```

FoMo is **not published on PyPI yet**. This is what the install will look like:

```bash
pip install 'fomo[client]'   # not on PyPI yet
```

Construct a client, call it, then close the session:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
print(client.health())  # status='ok' error=None
print(client.models())  # loaded ids only
print(client.stats())
client.close()
```

`with Client(...)` also closes the session for you:

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000", timeout=120.0) as client:
    print(client.models())
```

Default timeout is 60s. Hub models can need longer — pass `timeout=` as above.

## Request fields

Long tables plus roles, not a 1-d `y` vector. Same fields on JSON and `Client.forecast(...)`.

| field | |
| --- | --- |
| `past` | required. one row per timestamp |
| `fh` | required. steps ahead (`> 0`) |
| `time` | optional. timestamp column; omitted → first column of `past` |
| `target` | optional. always becomes a list; omitted → remaining `past` columns |
| `model` | optional. default `"naive"`; must be loaded |
| `future` | optional. future timestamps (and extra columns; see [covariates](#covariates)) |
| `static` | optional. one row of static features, broadcast over time |
| `quantiles` | optional. e.g. `[0.1, 0.5, 0.9]`; estimator must support it |

Panel (`series_id`) is not supported.

## Data format

`past`, `future`, `static`, `predictions`, and `quantiles` accept any of these shapes. JSON typically uses a column dict or a row matrix. The Python client also takes pandas, polars, pyarrow, and Narwhals. **Whatever you pass as `past` is what `predictions` / `quantiles` come back as.**

Snippets below assume a connected client:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
```

**Column dict** (name → list of equal length) — used in the [HTTP](#post-forecast) example above and in [univariate](#univariate-forecast) below.

**Row matrix:**

```python
past = {
    "columns": ["timestamp", "sales"],
    "data": [
        ["2024-01-01", 120],
        ["2024-01-02", 135],
        ["2024-01-03", 128],
        ["2024-01-04", 142],
        ["2024-01-05", 138],
    ],
}
```

**pandas** — see [covariates](#covariates).

**polars** — see [quantiles](#quantiles). Requires `pip install polars` (the `polars` package, not FoMo).

**pyarrow** Table:

```python
import pyarrow as pa

past = pa.table(
    {
        "timestamp": [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ],
        "sales": [120.0, 135.0, 128.0, 142.0, 138.0],
    }
)
result = client.forecast(
    past=past, time="timestamp", target=["sales"], fh=3, model="ttm-r3-52-16"
)
type(result.predictions)  # pyarrow.Table
```

**Narwhals** (stays Narwhals, same backend as `past`):

```python
import narwhals as nw
import pandas as pd

past = nw.from_native(
    pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "sales": [120, 135, 128, 142, 138],
        }
    )
)
result = client.forecast(
    past=past, time="timestamp", target=["sales"], fh=3, model="ttm-r3-52-16"
)
type(result.predictions)  # narwhals.DataFrame
```

You can omit `time` and `target` when the first column is time and the rest are targets:

```python
result = client.forecast(past=past, fh=3, model="naive")
```

## Univariate forecast

curl (JSON, column dict):

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
    "model": "ttm-r3-52-16"
  }'
```

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [135.62701416015625, 136.48983764648438, 139.23500061035156]
  },
  "quantiles": null,
  "model": "ttm-r3-52-16",
  "request_id": "…"
}
```

Same fields on the client, row-matrix in → row-matrix out:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
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
    model="toto-2.0-4m",
)
print(result.predictions)
client.close()
# {'columns': ['timestamp', 'sales'],
#  'data': [[Timestamp('2024-01-06 00:00:00'), 137.76…], …]}
```

`naive` is a drift `NaiveForecaster` — that is the pipe with no download. Swap `model` to any loaded id (`chronos-2`, `timesfm-2.5`, `ttm-r3-52-16`, `toto-2.0-4m`, …). Some ids need a longer history than the 5-row toy series — `mantis-8m` requires more observations than its `context_length` (127).

## Covariates

`static` is one row, broadcast over time as exogenous `X`. `future` is optional; when `static` is set it supplies the future **index** (must include `time`). Extra columns on `past` / `future` are accepted on the wire; the current sktime converter does not map them onto `X` — only the first `static` row is broadcast.

pandas in → pandas out. A store-level monthly series with several static attributes and a planned future calendar:

```python
import pandas as pd
from fomo.client import Client

past = pd.DataFrame(
    {
        "date": pd.date_range("2023-01-01", periods=12, freq="MS"),
        "sales": [120, 135, 128, 142, 150, 161, 155, 168, 173, 181, 195, 210],
        "price": [
            9.99,
            9.49,
            9.99,
            8.99,
            9.99,
            8.49,
            9.99,
            8.99,
            9.49,
            9.99,
            8.99,
            9.99,
        ],
        "promo": [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
    }
)
future = pd.DataFrame(
    {
        "date": pd.date_range("2024-01-01", periods=3, freq="MS"),
        "price": [8.99, 9.99, 9.49],
        "promo": [1, 0, 1],
    }
)
static = pd.DataFrame(
    {
        "store_type": ["urban"],
        "region": ["EU-west"],
        "floor_sqm": [420],
        "n_skus": [18],
    }
)

client = Client("http://127.0.0.1:8000", timeout=120.0)
result = client.forecast(
    past=past,
    future=future,
    static=static,
    time="date",
    target=["sales"],
    fh=3,
    model="chronos-2",
)
print(type(result.predictions))  # pandas.DataFrame
print(result.predictions)
client.close()
#         date  sales
# 0 2024-01-01  215.0
# 1 2024-02-01  226.0
# 2 2024-03-01  230.0
```

`target` can be a list of several columns if the loaded estimator accepts multivariate `y`.

## Quantiles

Add `quantiles=[0.1, 0.5, 0.9]`. Columns come back flattened: `{variable}_{alpha}` (often positional `0`, e.g. `0_0.1`). The estimator must implement `predict_quantiles`; otherwise the request fails.

polars in → polars out, on a Hub model that supports quantiles. Install polars yourself (`pip install polars`); it is not a FoMo extra.

```python
import polars as pl
from fomo.client import Client

past = pl.DataFrame(
    {
        "month": [
            "2023-01-01",
            "2023-02-01",
            "2023-03-01",
            "2023-04-01",
            "2023-05-01",
            "2023-06-01",
            "2023-07-01",
            "2023-08-01",
            "2023-09-01",
            "2023-10-01",
            "2023-11-01",
            "2023-12-01",
        ],
        "sales": [120, 135, 128, 142, 150, 161, 155, 168, 173, 181, 195, 210],
    }
)

client = Client("http://127.0.0.1:8000", timeout=120.0)
result = client.forecast(
    past=past,
    time="month",
    target=["sales"],
    fh=3,
    quantiles=[0.1, 0.5, 0.9],
    model="timesfm-2.5",
)
print(type(result.predictions))  # polars.DataFrame
print(result.predictions)
print(result.quantiles)
client.close()
# predictions: month / sales ≈ 217.25, 233.56, 243.88
# quantiles columns: month, 0_0.1, 0_0.5, 0_0.9
```

`predictions` stays the point forecast. `quantiles` is a second table, or `null` / `None` when the field was omitted. `naive` supports the same `quantiles=` call with no Hub download.
