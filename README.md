# FoMo

[![Documentation Status](https://readthedocs.org/projects/fomo/badge/?version=latest)](https://fomo.readthedocs.io/en/latest/?badge=latest)

Time series foundation model inference server. Load models once, forecast over HTTP or the Python client.
See the [documentation](https://fomo.readthedocs.io) for the server, client, models, dashboard, and Docker images.

Nothing is loaded by default: a bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models`. `GET /models` lists only what this process loaded.

| image | use |
| --- | --- |
| [`geetu040/fomo:sktime`](https://hub.docker.com/r/geetu040/fomo) | registry models (Chronos, TimesFM, TTM, Toto, Mantis, …) |
| [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) | `naive` only; tests and light workflows |

# Quick start

**Start the server**

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

or from source:

```bash
git clone git@github.com:sktime/fomo.git && cd fomo
uv sync --all-extras
uv run fomo serve --host 127.0.0.1 --port 8000 \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

**Forecast**

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

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
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
    model="timesfm-2.5",
)
print(result.predictions)
client.close()
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [135.89…, 136.19…, 136.59…]}
```

Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) · Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Some registry ids (`naive` needs no download): `chronos-2`, `timesfm-2.5`, `ttm-r3-52-16`, `toto-2.0-4m`, `mantis-8m`, `kronos`, `moirai-2`, `flowstate`, `tirex`. The full catalog is in the [docs](https://fomo.readthedocs.io).

#### Getting started

Here's a minimal setup to get started fast, from the repo directory:

##### uv
```bash
uv sync --extra server
uv run fomo serve --load-models naive
```

##### pip
```bash
pip install -e '.[server]'
fomo serve --load-models naive
```

Then run your request in another terminal, e.g. via curl:
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
Or via Python (install the `client` extra first: `uv sync --extra server --extra client` or `pip install -e '.[server,client]'`):
```python
import httpx2 as httpx

SERVER_URL = "http://127.0.0.1:8000"
response = httpx.post(f"{SERVER_URL}/forecast", json={
    "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138],
    },
    "time": "timestamp",
    "target": ["sales"],
    "fh": 3,
    "model": "naive",
})
response.raise_for_status()
print(response.json())
```

If you want to use foundation models, stop the server and install the additional requirements, e.g. for Chronos:

(uv)
```bash
uv sync --extra server --extra chronos
uv run fomo serve --load-models naive chronos-2
```

(pip)
```bash
pip install -e '.[server,chronos]'
fomo serve --load-models naive chronos-2
```
Then run the request from above using `"model": "chronos-2"`.
