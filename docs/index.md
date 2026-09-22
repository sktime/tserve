<div class="tserve-hero" markdown>

# TServe

Time series serving for foundation models. Load extra models you name, keep them warm, and predict from `curl` or `python`.
{ .tserve-hero__tagline }

[Quick start](#quick-start){ .md-button .md-button--primary }
[How it fits together](overview.md){ .md-button }

</div>

TServe is a process you start, not a hosted API. It loads time-series foundation models into one server and answers predict requests from a browser, `curl` or `python`. Dashboard, OpenAPI, and `/predict` all belong to that process.

The [catalog](models/index.md) covers the families you would reach for first: Chronos, Chronos Bolt, TTM, TimesFM, Moirai, Toto, TiRex, FlowState, Kronos, Mantis, Lag-Llama. TServe always loads a `naive` baseline so you can sanity-check a pipeline before any weights are downloaded; name extra models for a real forecast.

Start it with [uv or pip](server/pip.md) or from a [Docker image](server/docker.md), on CPU or GPU. Then predict over [HTTP](client/http.md) from any language, or from Python with the [client](client/python.md), which takes your dict, pandas, polars, or pyarrow table and hands the same type back. Point a browser at TServe for a [dashboard](server/dashboard.md) that plots predictions and shows what is loaded.

Models stay warm in the process, so the download and load cost is paid once at startup rather than on every request.

## Quick start

### Start the server

**Use Docker**

Pull the `hub` image and load two registry models: `chronos_bolt` and `ttm_r3`.

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
```

Every model except `naive` downloads a checkpoint from Hugging Face on first load. Pass [`-e HF_TOKEN`](server/docker.md#hugging-face-token) so that download is not rate-limited, [mount the Hub cache](server/docker.md#keep-weights-between-runs) to reuse the weights next time, and reach for a [`*-gpu` tag](server/docker.md#gpu-images) with `--gpus all` on an NVIDIA host. `:hub` is one tag; Chronos-2, Moirai, and the rest need a [different image](server/docker.md#choose-which-models-to-load).

**Install with uv or pip**

Python >= 3.12. The `server` extra is enough for `naive`; add a [family extra](models/index.md#dependencies) for Hub models. Editable installs from a clone: [From source](server/source.md).

=== "uv"

    ```bash
    uv pip install "tserve[server,hub]"
    uv run tserve chronos_bolt ttm_r3
    ```

=== "pip"

    ```bash
    pip install "tserve[server,hub]"
    tserve chronos_bolt ttm_r3
    ```

    The `gpu` extra does not work with pip. This install already pulls CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](server/pip.md#gpu).

Once the process is up, the terminal prints the URLs:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

`GET /models` lists the models this process actually loaded, not the full [catalog](models/index.md). `--host`, `--port`, and `--log-level` are the other [CLI flags](reference/cli.md#flags).

Leftover positionals can also take an sktime [craft spec](server/craft-specs.md) written as `id=spec`, or a saved `.zip` from a [directory of models](server/models-dir.md). To serve an estimator you configured yourself, start the server from Python with a [live object](server/live-objects.md).

### Predict

A request is a table plus the roles of its columns:

- `past` — history as a **table**: one row per timestamp, with a time column, one or more target columns, and any feature columns
- `time`, `target` — which column holds timestamps, and which ones to forecast
- `fh` — how many steps ahead
- `model` — a model this process loaded (`chronos_bolt` here; `ttm_r3` is also loaded above)

Three more fields are optional. Add [`quantiles`](client/data.md#quantiles) for prediction intervals from models that support them, or [`future` and `static`](client/data.md#future-and-static-data) for covariates you already know. The full contract — formats, defaults, and limits — is the [data specification](client/data.md).

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
      "model": "chronos_bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
    ```

Three predicted days come back, plus the model that served them:

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00", "2024-01-07T00:00:00", "2024-01-08T00:00:00"],
    "sales": [139.96, 138.93, 138.26]
  },
  "quantiles": null,
  "model": "chronos_bolt",
  "request_id": "…"
}
```

`past` can also be [row-oriented](client/data.md#table-formats), with `columns` and `data` instead of one list per column. Leave out `time` and `target` and TServe [infers them](client/data.md#column-inference) from column order. A request it cannot serve comes back as a 400 or 422 [error](reference/errors.md) carrying a message and the `request_id`.

**From `python`**

The client takes the same fields as keywords and sends Arrow instead of JSON. Install the `client` extra:

=== "uv"

    ```bash
    uv pip install "tserve[client]"
    ```

=== "pip"

    ```bash
    pip install "tserve[client]"
    ```

```python
from tserve.client import Client

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
        model="chronos_bolt",
    )

print(result.predictions)
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [139.96…, 138.93…, 138.26…]}
```

`past` went in as a dict of columns, so `predictions` comes back as one. Pass pandas, polars, or pyarrow and you get that type back instead — see [Python](client/python.md). A pandas frame that keeps time in its [index](client/python.md#use-an-indexed-pandas-frame) works too, and the predictions come back indexed the same way.

The process answers more than `/predict`. Its browser [dashboard](server/dashboard.md) plots a forecast from a sample series or a CSV you drop on it, while [`GET /models` and `GET /stats`](client/http.md#inspect-the-server) report what is loaded and how it is doing.

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

    Which registry models exist and which extra each one needs.

    [:octicons-arrow-right-24: Models](models/index.md)

-   :material-api:{ .lg .middle } **Send predictions**

    ---

    Request and response shapes over JSON, or the Python client.

    [:octicons-arrow-right-24: HTTP](client/http.md) or [Python](client/python.md)

-   :material-table-column:{ .lg .middle } **Data specification**

    ---

    Every request field, table format, and response shape.

    [:octicons-arrow-right-24: Data specification](client/data.md)

</div>
