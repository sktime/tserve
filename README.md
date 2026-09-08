# FoMo

[![Documentation Status](https://readthedocs.org/projects/fomo/badge/?version=latest)](https://fomo.readthedocs.io/en/latest/?badge=latest)

Time series foundation model inference server. Load models once, forecast over HTTP or the Python client.
See the [documentation](https://fomo.readthedocs.io) for the server, client, models, dashboard, and Docker images.

Nothing is loaded by default: a bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models`. `GET /models` lists only what this process loaded.

| image | use |
| --- | --- |
| [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) | `naive` only |
| [`geetu040/fomo:hub`](https://hub.docker.com/r/geetu040/fomo) | TTM, TimesFM 2.x, Chronos Bolt/T5 |
| [`geetu040/fomo:full`](https://hub.docker.com/r/geetu040/fomo) | every family in the catalog |

Family tags (`chronos`, `granite`, `moirai`, `tirex`, `toto`, `mantis`, `kronos`) and `*-gpu` variants: [docs](https://fomo.readthedocs.io/en/latest/models/).

# Quick start

**Start the server**

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Or from this repo (Python >= 3.12). FoMo is not on PyPI yet.

uv:

```bash
git clone https://github.com/sktime/fomo.git && cd fomo
uv sync --extra server --extra client --extra hub
uv run fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

pip:

```bash
git clone https://github.com/sktime/fomo.git && cd fomo
pip install -e ".[server,client,hub]"
fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

**Forecast**

`POST /forecast` (GET returns 405). `past` is a table: one row per timestamp, with a time column and target columns.

```bash
curl -s http://127.0.0.1:8000/forecast -H 'Content-Type: application/json' -d '{"past": {"timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"], "sales": [120, 135, 128, 142, 138]}, "time": "timestamp", "target": ["sales"], "fh": 3, "model": "chronos-bolt-tiny"}'
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
    model="chronos-bolt-tiny",
)
print(result.predictions)
client.close()
```

Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) · Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

# Getting started (naive only)

Minimal install from the repo directory. `naive` needs no Hugging Face download.

uv:

```bash
uv sync --extra server
uv run fomo serve --load-models naive
```

pip:

```bash
pip install -e ".[server]"
fomo serve --load-models naive
```

Then in another terminal:

```bash
curl -s http://127.0.0.1:8000/forecast -H 'Content-Type: application/json' -d '{"past": {"timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"], "sales": [120, 135, 128, 142, 138]}, "time": "timestamp", "target": ["sales"], "fh": 3, "model": "naive"}'
```

For the Python client, also install the `client` extra (`uv sync --extra server --extra client` or `pip install -e ".[server,client]"`).

To load foundation models, stop the server and add the matching extra, for example Chronos-2. Then use `"model": "chronos-2"` in the request above.

```bash
uv sync --extra server --extra chronos
uv run fomo serve --load-models naive chronos-2
```

```bash
pip install -e ".[server,chronos]"
fomo serve --load-models naive chronos-2
```

Set `HF_TOKEN` if Hugging Face rate-limits unauthenticated downloads. The extras table and full catalog are in the [docs](https://fomo.readthedocs.io).
