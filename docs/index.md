<div class="fomo-hero" markdown>

# FoMo

Time-series Foundation Models behind one server. Load the models you name, keep them warm, and forecast from `curl` or `python`.
{ .fomo-hero__tagline }

[Quick start](#quick-start){ .md-button .md-button--primary }
[How it fits together](overview.md){ .md-button }

</div>

FoMo is a process you start, not a hosted API. It loads time-series foundation models into one server and answers forecast requests from a browser, `curl` or `python`. Dashboard, OpenAPI, and `/forecast` all belong to that process.

The [catalog](models/catalog.md) covers the families you would reach for first: Chronos, Chronos Bolt, TTM, TimesFM, Moirai, Toto, TiRex, FlowState, Kronos, Mantis, Lag-Llama, plus a naive baseline to sanity-check a pipeline before any weights are downloaded. You [name the ids you want](models/index.md); the server loads those and leaves the rest alone.

Start it [from source](server/index.md) or from a [Docker image](server/docker.md), on CPU or GPU. Then forecast over [HTTP](client/http.md) from any language, or from Python with the [client](client/python.md), which takes your dict, pandas, polars, or pyarrow table and hands the same type back. Point a browser at the server for a [dashboard](server/dashboard.md) that plots forecasts and shows what is loaded.

Models stay warm in the process, so the download and load cost is paid once at startup rather than on every request.

## Quick start

**Start the server**

Pull the `hub` image and load a handful of registry ids: `naive`, `chronos-bolt-tiny`, `ttm-r3-512-30`.

```bash
docker run -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Or clone the repo and start from source. The `server` extra is enough for `naive`; add a [family extra](server/index.md#dependencies) for Hub models.

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra hub
    uv run fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,hub]"
    fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

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

Or the Python client (Arrow on the wire, your table type back). Install the `client` extra:

=== "uv"

    ```bash
    uv sync --extra client
    ```

=== "pip"

    ```bash
    pip install -e ".[client]"
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
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [139.96…, 138.93…, 138.26…]}
```

## Where to next

<div class="grid cards" markdown>

-   :material-map-outline:{ .lg .middle } **Overview**

    ---

    How transports, canonical frames, and executors fit together.

    [:octicons-arrow-right-24: Architecture](overview.md)

-   :material-server:{ .lg .middle } **Run a server**

    ---

    Install extras, pick a Docker tag, and check the flags.

    [:octicons-arrow-right-24: Install and serve](server/index.md)

-   :material-cube-outline:{ .lg .middle } **Load models**

    ---

    Which registry ids exist and which extra each one needs.

    [:octicons-arrow-right-24: Models](models/index.md)

-   :material-api:{ .lg .middle } **Send forecasts**

    ---

    Request and response shapes over JSON, or the Python client.

    [:octicons-arrow-right-24: HTTP](client/http.md) or [Python](client/python.md)

</div>
