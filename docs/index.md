<div class="fomo-hero" markdown>

# FoMo

Time-series Foundation Models behind one server. Load the models you name, keep them warm, and predict from `curl` or `python`.
{ .fomo-hero__tagline }

[Quick start](#quick-start){ .md-button .md-button--primary }
[How it fits together](overview.md){ .md-button }

</div>

FoMo is a process you start, not a hosted API. It loads time-series foundation models into one server and answers predict requests from a browser, `curl` or `python`. Dashboard, OpenAPI, and `/predict` all belong to that process.

The [catalog](models/index.md) covers the families you would reach for first: Chronos, Chronos Bolt, TTM, TimesFM, Moirai, Toto, TiRex, FlowState, Kronos, Mantis, Lag-Llama, plus a naive baseline to sanity-check a pipeline before any weights are downloaded. You name the ids you want; the server loads those and leaves the rest alone.

Start it [from source](server/source.md) or from a [Docker image](server/docker.md), on CPU or GPU. Then predict over [HTTP](client/http.md) from any language, or from Python with the [client](client/python.md), which takes your dict, pandas, polars, or pyarrow table and hands the same type back. Point a browser at the server for a [dashboard](server/dashboard.md) that plots predictions and shows what is loaded.

Models stay warm in the process, so the download and load cost is paid once at startup rather than on every request.

## Quick start

### Start the server

**Use Docker**

Pull the `hub` image and load two registry ids: `chronos-bolt` and `timesfm-2.5`.

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt timesfm-2.5
```

**Build from source**

Or clone the repo and start from source. The `server` extra is enough for `naive`; add a [family extra](models/index.md#dependencies) for Hub models.

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra hub
    uv run fomo serve --load-models chronos-bolt timesfm-2.5
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,hub]"
    fomo serve --load-models chronos-bolt timesfm-2.5
    ```

    The `gpu` extra does not work with pip. This install already pulls CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](server/source.md#gpu).

Once the process is up, the terminal prints the URLs:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Predict

A request is a table plus the roles of its columns:

- `past` — history as a **table**: one row per timestamp, with a time column, one or more target columns, and any feature columns
- `time`, `target` — which column holds timestamps, and which ones to forecast
- `fh` — how many steps ahead
- `model` — an id this process loaded (`chronos-bolt` here; `timesfm-2.5` is also loaded above)

**From `curl`**

Five days of sales, three days ahead. Copy the tab for your shell (`curl.exe` on Windows so PowerShell does not use `Invoke-WebRequest`).

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "chronos-bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "chronos-bolt"
    }'
    ```

Three predicted days come back, plus the id that served them:

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [139.96, 138.93, 138.26]
  },
  "quantiles": null,
  "model": "chronos-bolt",
  "request_id": "…"
}
```

**From `python`**

The client takes the same fields as keywords and sends Arrow instead of JSON. Install the `client` extra:

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

past = {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    "sales": [120, 135, 128, 142, 138],
}

with Client("http://127.0.0.1:8000") as client:
    result = client.predict(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="chronos-bolt",
    )

print(result.predictions)
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [139.96…, 138.93…, 138.26…]}
```

`past` went in as a dict of columns, so `predictions` comes back as one. Pass pandas, polars, or pyarrow and you get that type back instead — see [Python](client/python.md).

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

-   :material-cube-outline:{ .lg .middle } **Catalog**

    ---

    Which registry ids exist and which extra each one needs.

    [:octicons-arrow-right-24: Models](models/index.md)

-   :material-api:{ .lg .middle } **Send predictions**

    ---

    Request and response shapes over JSON, or the Python client.

    [:octicons-arrow-right-24: HTTP](client/http.md) or [Python](client/python.md)

</div>
