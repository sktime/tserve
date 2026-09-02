# FoMo

[![Documentation Status](https://readthedocs.org/projects/fomo/badge/?version=latest)](https://fomo.readthedocs.io/en/latest/?badge=latest)

Time series foundation model inference server. Load models once, forecast over HTTP or the Python client.
See the [documentation](https://fomo.readthedocs.io) for the server, client, models, dashboard, and Docker images.

Nothing is loaded by default: a bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models`. `GET /models` lists only what this process loaded.

| image | use |
| --- | --- |
| [`geetu040/fomo:sktime`](https://hub.docker.com/r/geetu040/fomo) | registry models (Chronos, TimesFM, TTM, …) |
| [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) | `naive` only; tests and light workflows |

# Quick start

**Start the server**

```bash
docker run --rm -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2
```

or from source:

```bash
git clone git@github.com:sktime/fomo.git && cd fomo
uv sync --extra server --extra sktime-lite --extra client
uv run fomo serve --host 127.0.0.1 --port 8000 --load-models naive
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
```

Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) · Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Some registry ids (`naive` needs no download): `chronos-2`, `timesfm-2.5`, `ttm-r3-52-16`, `toto-2.0-4m`, `mantis-8m`, `kronos`, `moirai-2`, `flowstate`, `tirex`. The full catalog is in the [docs](https://fomo.readthedocs.io).
