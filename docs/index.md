<div class="fomo-hero" markdown>

# FoMo

Time-series foundation models behind one HTTP server. Load the models you name,
keep them warm, and forecast from `curl` or Python.
{ .fomo-hero__tagline }

[Quick start](#quick-start){ .md-button .md-button--primary }
[How it fits together](overview.md){ .md-button }

</div>

FoMo is a time-series foundation-model inference server. Load selected models once, keep them warm, and forecast over HTTP or the Python client. It is not a training library.

Nothing is loaded by default. A bare `fomo serve` starts with an empty model list. Name registry ids with `--load-models`. `GET /models` lists only what this process loaded, not the full [catalog](models/catalog.md).

Images are split by model family so you do not pull every estimator extra. The image `CMD` loads `naive` if you pass no extra arguments. That is an image default, not the Python default.

| tag | loads |
| --- | --- |
| [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) | `naive` only |
| [`geetu040/fomo:hub`](https://hub.docker.com/r/geetu040/fomo) | `base` + TTM + TimesFM 2.x + Chronos Bolt/T5 |
| [`geetu040/fomo:full`](https://hub.docker.com/r/geetu040/fomo) | every family in the catalog |

Family tags (`chronos`, `granite`, `moirai`, `tirex`, `toto`, `mantis`, `kronos`) and `*-gpu` variants are listed on the [Docker](server/docker.md) page.

## Quick start

**Start the server**

Pull the `hub` image and load a handful of registry ids:

```bash
docker run -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Or clone the repo and start from source. Python >= 3.12. The `server` extra is enough for `naive`; add a [family extra](server/index.md#dependencies) for Hub models.

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra client --extra hub
    uv run fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,client,hub]"
    fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

FoMo is **not on PyPI yet**. The `pip` line installs from this clone.

Once the process is up, the terminal prints the URLs:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

There is no hosted FoMo API. Every URL is the process you started.

## Forecast

`POST /forecast` (a GET returns HTTP 405). `past` is a **table**: one row per timestamp, with a time column and one or more target columns — not a 1-d vector and not a pandas index.

`"model"` must be one of the ids this process loaded (`chronos-bolt-tiny` below; `ttm-r3-512-30` and `naive` also work).

```bash
curl -s http://127.0.0.1:8000/forecast -H 'Content-Type: application/json' -d '{"past": {"timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"], "sales": [120, 135, 128, 142, 138]}, "time": "timestamp", "target": ["sales"], "fh": 3, "model": "chronos-bolt-tiny"}'
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

Or the Python client (install the `client` extra; Arrow on the wire, your table type back):

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
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [139.96…, 138.93…, 138.26…]}
```

Next: [Overview](overview.md) for how the pieces fit, then [server](server/index.md), [models](models/index.md), [HTTP](client/http.md), and [Python](client/python.md).
