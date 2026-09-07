# FoMo

FoMo is a time-series foundation-model inference server. Load selected models once, keep them warm, and forecast over HTTP or the Python client. It is not a training library.

Nothing is loaded by default. A bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models` to load them. `GET /models` lists only what this process loaded, not the full [catalog](walkthrough/models.md).

Two Docker images are published:

- [`geetu040/fomo:sktime`](https://hub.docker.com/r/geetu040/fomo) — registry models (Chronos, TimesFM, TTM, Toto, Mantis, …)
- [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) — `naive` only, for tests and light workflows

The image `CMD` loads `naive` if you pass no extra arguments. That is an image default, not the Python default.

# Quick start

**Start the server**

Pull the sktime image and load a handful of registry ids:

```bash
docker run -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Or clone the repo and start from source:

```bash
git clone https://github.com/sktime/fomo.git && cd fomo
uv sync --extra server --extra client --extra hub
uv run fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Once the process is up:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

There is no hosted FoMo API. Every URL is the process you started.

**Forecast**

JSON over HTTP (`naive` needs no Hub download; swap `"model"` for any loaded id):

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
    "model": "chronos-bolt-tiny"
  }'
```

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [139.96, 138.93, 138.26]
  },
  "quantiles": null,
  "model": "chronos-bolt-tiny",
  "request_id": "…"
}
```

`naive` is `NaiveForecaster(strategy="drift")`, so the point forecast continues the slope rather than repeating the last value.

Or the Python client (same package, Arrow on the wire, your table type back):

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

Next: [Overview](overview.md) for how the pieces fit, then the [server](walkthrough/server.md), [models](walkthrough/models.md), and [client](walkthrough/client.md) walkthroughs.
