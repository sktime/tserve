# FoMo

Time series foundation model inference server. Load models once, forecast over HTTP or the Python client.

Nothing is loaded by default: a bare `fomo serve` starts with an empty model list. Name registry aliases with `--load-models` / `load_models` to load them. `dummy` is a `NaiveForecaster` (no download); the rest pull Hugging Face weights at load time. `GET /models` lists only what this process loaded.

| alias | estimator | alias | estimator |
| --- | --- | --- | --- |
| `dummy` | `NaiveForecaster` | `chronos2` | `Chronos2Forecaster` |
| `chronos` | `ChronosForecaster` | `kronos` | `KronosForecaster` |
| `moirai2` | `Moirai2Forecaster` | `moirai` | `MOIRAIForecaster` |
| `ttm` | `TinyTimeMixerForecaster` | `tirex` | `TiRexForecaster` |
| `timesfm2.5` | `TimesFM2Forecaster` | `timesfm` | `TimesFMForecaster` |
| `toto` | `TotoForecaster` | `toto2` | `Toto2Forecaster` |
| `flowstate` | `FlowStateForecaster` | `patchtsmixer` | `PatchTSMixerForecaster` |
| `patchtst` | `PatchTSTForecaster` | `windfm` | `WindFMForecaster` |
| `aurora` | `AuroraForecaster` | `lagllama` | `LagLlamaForecaster` |
| `falconx` | `FalconXForecaster` | `falcontst` | `FalconTSTForecaster` |
| `timemoe` | `TimeMoEForecaster` | `sundial` | `SundialForecaster` |
| `timer` | `TimerForecaster` | `timers1` | `TimerS1Forecaster` |
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
  fomo serve --host 0.0.0.0 --port 8000 --load-models dummy chronos2
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
  fomo serve --host 0.0.0.0 --port 8000 --load-models dummy chronos2
```

Or build this repo’s `Dockerfile` from source (Python 3.13, `uv sync --frozen`):

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
docker build -t fomo:local .
docker run --rm -p 8000:8000 fomo:local \
  uv run --frozen fomo serve --host 0.0.0.0 --port 8000 --load-models dummy
```

### From source

Python >= 3.12. Uses [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
uv sync
uv run fomo serve --host 0.0.0.0 --port 8000 --load-models dummy
```

Same thing after a normal install:

```bash
uv pip install -e .
fomo serve --host 0.0.0.0 --port 8000 --load-models dummy chronos2
```

### CLI

```bash
fomo serve \
  --host 0.0.0.0 \
  --port 8000 \
  --load-models dummy chronos2 \
  --log-level info
```

| flag | default | |
| --- | --- | --- |
| `--load-models` | none | registry aliases to load |
| `--host` | `127.0.0.1` | use `0.0.0.0` in Docker |
| `--port` | `8000` | |
| `--log-level` | `info` | |

### Server SDK

```python
from fomo.server import Server

Server(load_models=["dummy"], host="0.0.0.0", port=8000).run()
```

Omitting `load_models` starts a server with no models, same as omitting `--load-models`. The FastAPI app is `server.app` if you want to mount it yourself:

```python
from fomo.server import Server

server = Server(load_models=["dummy", "chronos2"], host="127.0.0.1", port=8000)
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

Univariate, `dummy`, three daily steps:

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
    "freq": "D",
    "model": "dummy"
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
  "model": "dummy",
  "request_id": "..."
}
```

Quantiles (`dummy` only among the default aliases):

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
    "freq": "D",
    "quantiles": [0.1, 0.5, 0.9],
    "model": "dummy"
  }'
```

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
    "freq": "MS",
    "model": "dummy"
  }'
```

Swap `"model": "chronos2"` on a server that loaded that alias. Unlisted columns are ignored. Omit empty role lists.

| field | required | |
| --- | --- | --- |
| `history` | yes | long table: one row per series × observed timestamp |
| `future` | if `known_future` is set | horizon covariates only, no targets, `horizon` timestamps per series |
| `static` | if static features exist | one row per series |
| `series_id` | no | key columns (MultiIndex order). omit for a single series |
| `time` | yes | timestamp column |
| `target` | yes | always a list |
| `known_future` | no | dynamic covariates in both `history` and `future` |
| `past_only` | no | history-only covariates (kept for later backends; not sktime `X`) |
| `horizon` | yes | steps to forecast |
| `freq` | no | pandas offset (`D`, `MS`, `H`, …). not inferred |
| `quantiles` | no | e.g. `[0.1, 0.5, 0.9]` |
| `params` | no | model-specific overrides |
| `model` | yes | loaded estimator alias |

Tables on JSON are `{ "columns": [...], "data": [[...], ...] }`.

### Python SDK

Install the same `fomo` package the server uses. Point it at a running `fomo serve`.

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000") as client:
    print(client.health())   # status='ok'
    print(client.models())   # aliases, executors, capabilities
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
        freq="D",
        model="dummy",
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
    freq="D",
    model="dummy",
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
        freq="D",
        model="dummy",  # or "chronos2" if that alias is loaded
    )

print(type(result.predictions))  # pandas.DataFrame
print(result.predictions)
```

Panel + covariates + quantiles, same kwargs as the JSON body:

```python
result = client.forecast(
    history=history_df,       # pandas / polars / {columns, data}
    future=future_df,         # required when known_future is set
    static=static_df,         # one row per series
    series_id=["store", "sku"],
    time="date",
    target=["sales"],
    known_future=["price", "promo"],
    past_only=["inventory"],
    horizon=2,
    freq="MS",
    quantiles=[0.1, 0.9],
    params={},
    model="dummy",
)
```
