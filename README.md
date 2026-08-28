# FoMo

Time series foundation model inference server. Load models once, forecast over HTTP or the Python client.
See [docs/](docs/index.md) for install, serving, the forecast API, the Python client, models, and architecture.

Nothing is loaded by default: a bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models` / `load_models` to load them. `naive` is a `NaiveForecaster` (no download); the rest pull Hugging Face weights at load time. `GET /models` lists only what this process loaded.

| id | estimator | id | estimator |
| --- | --- | --- | --- |
| `naive` | `NaiveForecaster` | `chronos-2` | `Chronos2Forecaster` |
| `chronos` | `ChronosForecaster` | `kronos` | `KronosForecaster` |
| `moirai-2` | `Moirai2Forecaster` | `moirai` | `MOIRAIForecaster` |
| `ttm` | `TinyTimeMixerForecaster` | `tirex` | `TiRexForecaster` |
| `timesfm-2.5` | `TimesFM2Forecaster` | `timesfm` | `TimesFMForecaster` |
| `toto` | `TotoForecaster` | `toto-2` | `Toto2Forecaster` |
| `flowstate` | `FlowStateForecaster` | `patchtsmixer` | `PatchTSMixerForecaster` |
| `patchtst` | `PatchTSTForecaster` | `windfm` | `WindFMForecaster` |
| `aurora` | `AuroraForecaster` | `lagllama` | `LagLlamaForecaster` |
| `falconx` | `FalconXForecaster` | `falcontst` | `FalconTSTForecaster` |
| `timemoe` | `TimeMoEForecaster` | `sundial` | `SundialForecaster` |
| `timer` | `TimerForecaster` | `timer-s1` | `TimerS1Forecaster` |
| `mira` | `MIRAForecaster` | `cisctsm` | `CiscoTSMForecaster` |
| `momentfm` | `MomentFMAnomalyDetector` | `tspulse` | `TSPulseAnomalyDetector` |

API docs once a server is up: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Server

Pick one way to run it. All of them expose the same API on `--host` / `--port`.

### Docker: pre-built image

```bash
docker run --rm -p 8000:8000 \
  docker.io/sktime/fomo:dl-py3.13 \
  fomo serve --host 0.0.0.0 --port 8000 --load-models naive chronos-2
```

### Docker: custom image

Add extra Python deps on top of the published image:

```dockerfile
FROM docker.io/sktime/fomo:dl-py3.13

RUN pip install my-package another-package
```

```bash
docker build -t my-fomo:custom .
docker run --rm -p 8000:8000 \
  my-fomo:custom \
  fomo serve --host 0.0.0.0 --port 8000 --load-models naive chronos-2
```

Or build this repo’s `Dockerfile` from source (Python 3.13, `uv sync`).
The image always installs `server` and `sktime-lite` and loads `naive` unless you pass `--load-models`.
Add heavier extras at build time (`sktime`, `pytorch-forecasting`):

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
docker build -t fomo:local .
docker run --rm -p 8000:8000 fomo:local
# or: docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
#     docker run --rm -p 8000:8000 fomo:sktime --load-models naive chronos-2
```

### From source

Python >= 3.12. Uses [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
uv sync
uv run fomo serve --host 0.0.0.0 --port 8000 --load-models naive
```

Same thing after a normal install:

```bash
uv pip install -e .
fomo serve --host 0.0.0.0 --port 8000 --load-models naive chronos-2
```

### CLI

```bash
fomo serve \
  --host 0.0.0.0 \
  --port 8000 \
  --load-models naive chronos-2 \
  --log-level info
```

| flag | default | |
| --- | --- | --- |
| `--load-models` | none | registry ids to load |
| `--host` | `127.0.0.1` | use `0.0.0.0` in Docker |
| `--port` | `8000` | |
| `--log-level` | `info` | |

### Server SDK

```python
from fomo.server import Server

Server(load_models=["naive"], host="0.0.0.0", port=8000).run()
```

Omitting `load_models` starts a server with no models, same as omitting `--load-models`. Ids resolve from the registry (`source="registry"`). You can pass a `(id, estimator)` pair (SDK only; the CLI still takes names):

```python
from fomo.server import Server
from sktime.forecasting.naive import NaiveForecaster

naive = NaiveForecaster()
Server(load_models=["chronos-2", ("naive", naive)], host="0.0.0.0", port=8000).run()
```

`GET /models` returns `{id, executor, source}` for each loaded model. `source` is `registry`, `directory`, or `object`.

The FastAPI app is `server.app` if you want to mount it yourself:

```python
from fomo.server import Server

server = Server(load_models=["naive", "chronos-2"], host="127.0.0.1", port=8000)
print(server.url)  # http://127.0.0.1:8000
# uvicorn.run(server.app, host=server.host, port=server.port)
server.run()
```

---

## Client

Wire: **JSON** (`Content-Type: application/json`) for curl and any HTTP client, **Arrow IPC** (`application/vnd.fomo.forecast+arrow`) for `fomo.client.Client`. Same `/forecast` body either way.

### HTTP

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}

curl -s http://127.0.0.1:8000/models
```

Univariate, `naive`, three daily steps:

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "time": "timestamp",
    "target": ["sales"],
    "history": {
      "columns": ["timestamp", "sales"],
      "data": [
        ["2024-01-01", 120],
        ["2024-01-02", 135],
        ["2024-01-03", 128],
        ["2024-01-04", 142],
        ["2024-01-05", 138]
      ]
    },
    "horizon": 3,
    "context": 5,
    "freq": "D",
    "model": "naive"
  }'
```

```json
{
  "predictions": {
    "columns": ["timestamp", "sales"],
    "data": [
      ["2024-01-06T00:00:00", 138.0],
      ["2024-01-07T00:00:00", 138.0],
      ["2024-01-08T00:00:00", 138.0]
    ]
  },
  "quantiles": null,
  "model": "naive",
  "request_id": "..."
}
```

### Quantiles on a real model

Add `quantiles` to get a probabilistic forecast. It works on some loaded ids
(`timesfm-2.5`, `flowstate`, `windfm`, `aurora`, `lagllama`, `toto`,
`toto-2`, `sundial`, `timer-s1`, `cisctsm`, `falconx`, and `naive`). Asking any other id for
quantiles fails with `503 model_unavailable` and the estimator's own message, e.g.
`ChronosForecaster does not have the capability to return quantile predictions.`

Start a server with a real foundation model. First start downloads weights from the Hub:

```bash
uv run fomo serve --host 0.0.0.0 --port 8000 --load-models timesfm-2.5
```

Twelve monthly observations, three months ahead, 10th/50th/90th percentiles:

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "time": "month",
    "target": ["sales"],
    "history": {
      "columns": ["month", "sales"],
      "data": [
        ["2023-01-01", 120],
        ["2023-02-01", 135],
        ["2023-03-01", 128],
        ["2023-04-01", 142],
        ["2023-05-01", 150],
        ["2023-06-01", 161],
        ["2023-07-01", 155],
        ["2023-08-01", 168],
        ["2023-09-01", 173],
        ["2023-10-01", 181],
        ["2023-11-01", 195],
        ["2023-12-01", 210]
      ]
    },
    "horizon": 3,
    "context": 12,
    "freq": "MS",
    "quantiles": [0.1, 0.5, 0.9],
    "model": "timesfm-2.5"
  }'
```

Real response from that request:

```json
{
  "predictions": {
    "columns": ["month", "sales"],
    "data": [
      ["2024-01-01T00:00:00", 217.24871826171875],
      ["2024-02-01T00:00:00", 233.55999755859375],
      ["2024-03-01T00:00:00", 243.87789916992188]
    ]
  },
  "quantiles": {
    "columns": ["index", "0_0.1", "0_0.5", "0_0.9"],
    "data": [
      ["2024-01-01T00:00:00", 217.5303192138672, 216.601318359375, 226.1812744140625],
      ["2024-02-01T00:00:00", 233.885498046875, 232.79592895507812, 240.87062072753906],
      ["2024-03-01T00:00:00", 245.2987060546875, 243.27342224121094, 251.66632080078125]
    ]
  },
  "model": "timesfm-2.5",
  "request_id": "..."
}
```

`predictions` holds the point forecast. `quantiles` is a flattened sktime `predict_quantiles`
frame: first column is the timestamp, then one `<variable>_<quantile>` column per requested
level (the variable is positional, hence `0`). Quantiles are model output and are not sorted
or clipped, so they are not guaranteed monotonic across levels.

Same request through the Python client, which keeps your dataframe type:

```python
import pandas as pd
from fomo.client import Client

history = pd.DataFrame(
    {
        "month": pd.date_range("2023-01-01", periods=12, freq="MS"),
        "sales": [120, 135, 128, 142, 150, 161, 155, 168, 173, 181, 195, 210],
    }
)

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        history=history,
        time="month",
        target=["sales"],
        horizon=3,
        context=12,
        freq="MS",
        quantiles=[0.1, 0.5, 0.9],
        model="timesfm-2.5",
    )

print(result.predictions)
#        month       sales
# 0 2024-01-01  217.248718
# 1 2024-02-01  233.559998
# 2 2024-03-01  243.877899

print(result.quantiles)
#        index       0_0.1       0_0.5       0_0.9
# 0 2024-01-01  217.530319  216.601318  226.181274
# 1 2024-02-01  233.885498  232.795929  240.870621
# 2 2024-03-01  245.298706  243.273422  251.666321
```

`flowstate` is a lighter alternative if you want a faster download: swap
`--load-models flowstate` and `"model": "flowstate"`.

Panel (`store` × `sku`) plus known-future covariates. `future` has exactly `horizon` timestamps per series, no targets:

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "series_id": ["store", "sku"],
    "time": "date",
    "target": ["sales"],
    "known_future": ["price", "promo"],
    "history": {
      "columns": ["store", "sku", "date", "sales", "price", "promo"],
      "data": [
        ["A", 1, "2023-01-01", 100, 9.99, 0],
        ["A", 1, "2023-02-01", 110, 9.49, 1],
        ["A", 1, "2023-03-01", 105, 9.99, 0],
        ["A", 1, "2023-04-01", 120, 8.99, 1],
        ["B", 2, "2023-01-01", 80, 12.5, 0],
        ["B", 2, "2023-02-01", 90, 12.0, 1],
        ["B", 2, "2023-03-01", 85, 12.5, 0],
        ["B", 2, "2023-04-01", 95, 11.5, 1]
      ]
    },
    "future": {
      "columns": ["store", "sku", "date", "price", "promo"],
      "data": [
        ["A", 1, "2023-05-01", 8.99, 1],
        ["A", 1, "2023-06-01", 9.99, 0],
        ["B", 2, "2023-05-01", 11.0, 1],
        ["B", 2, "2023-06-01", 12.5, 0]
      ]
    },
    "static": {
      "columns": ["store", "sku", "store_type"],
      "data": [["A", 1, "urban"], ["B", 2, "rural"]]
    },
    "horizon": 2,
    "context": 4,
    "freq": "MS",
    "model": "naive"
  }'
```

Swap `"model": "chronos-2"` on a server that loaded that id. Unlisted columns are ignored. Omit empty role lists.

| field | required | |
| --- | --- | --- |
| `history` | yes | long table: one row per series × observed timestamp |
| `future` | if `known_future` is set | horizon covariates only, no targets, `horizon` timestamps per series |
| `static` | if static features exist | one row per series |
| `series_id` | no | key columns (MultiIndex order). omit for a single series |
| `time` | yes | timestamp column |
| `target` | yes | always a list |
| `known_future` | no | dynamic covariates in both `history` and `future` |
| `horizon` | yes | steps to forecast |
| `context` | yes | context length (placeholder; ignored for now) |
| `freq` | no | pandas offset (`D`, `MS`, `H`, …). not inferred |
| `quantiles` | no | e.g. `[0.1, 0.5, 0.9]` |
| `params` | no | model-specific overrides |
| `model` | yes | loaded estimator id |

Tables on JSON are `{ "columns": [...], "data": [[...], ...] }`.

### Python SDK

Install the same `fomo` package the server uses. Point it at a running `fomo serve`.

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    print(client.health())  # status='ok'
    print(client.models())  # ids, executors, sources
```

JSON `{columns, data}` in, same shape out:

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        history={
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
        horizon=3,
        context=5,
        freq="D",
        model="naive",
    )

print(result.model, result.request_id)
print(result.predictions)
# {'columns': ['timestamp', 'sales'], 'data': [['2024-01-06T00:00:00', 138.0], ...]}
```

Column-oriented dict in, same layout out:

```python
result = client.forecast(
    history={
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "sales": [120, 135, 128],
    },
    time="timestamp",
    target=["sales"],
    horizon=2,
    context=3,
    freq="D",
    model="naive",
)
# result.predictions == {"timestamp": ["2024-01-04T00:00:00", ...], "sales": [128.0, 128.0]}
```

pandas / polars / pyarrow / Narwhals in, same native type out (Arrow on the wire):

```python
import pandas as pd
from fomo.client import Client

history = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "sales": [120, 135, 128, 142, 138],
    }
)

with Client("http://127.0.0.1:8000", timeout=60.0) as client:
    result = client.forecast(
        history=history,
        time="timestamp",
        target=["sales"],
        horizon=3,
        context=5,
        freq="D",
        model="naive",  # or "chronos-2" if that id is loaded
    )

print(type(result.predictions))  # pandas.DataFrame
print(result.predictions)
```

Panel + covariates + quantiles, same kwargs as the JSON body:

```python
result = client.forecast(
    history=history_df,  # pandas / polars / {columns, data}
    future=future_df,  # required when known_future is set
    static=static_df,  # one row per series
    series_id=["store", "sku"],
    time="date",
    target=["sales"],
    known_future=["price", "promo"],
    horizon=2,
    context=4,
    freq="MS",
    quantiles=[0.1, 0.9],
    params={},
    model="naive",
)
```
