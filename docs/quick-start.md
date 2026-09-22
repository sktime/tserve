# Quick start

Start a server with two models, confirm that it is ready, and send a forecast. If TServe is not installed yet, begin with [Installation](installation.md).

## 1. Start the server

**Docker is faster and preferred.** The image already carries the dependencies, and CPU vs GPU is a tag. The UV and Pip tabs assume you already installed `tserve[server,hub]`.

=== "Docker"

    === "CPU"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
        ```

    === "GPU"

        ```bash
        docker run --rm --gpus all -p 8000:8000 sktime/tserve:hub-gpu chronos_bolt ttm_r3
        ```

=== "uv"

    ```bash
    uv run tserve chronos_bolt ttm_r3
    ```

=== "pip"

    ```bash
    tserve chronos_bolt ttm_r3
    ```

The first start downloads model weights from Hugging Face. The terminal then prints the local URLs for the dashboard, Swagger UI, and ReDoc.

## 2. Check what loaded

`GET /models` reports models loaded by this process, not every model in the [catalog](models/index.md).

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/models
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/models
    ```

The response includes `naive`, which is always available as a test baseline, plus `chronos_bolt` and `ttm_r3`.

## 3. Send a prediction

This request sends five days of sales and asks `chronos_bolt` for the next three:

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

The response contains three predicted days and identifies the model that served them:

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

## 4. Try the Python client

Install the client in a separate environment if the calling application does not share the server environment:

=== "uv"

    ```bash
    uv pip install "tserve[client]"
    ```

=== "pip"

    ```bash
    pip install "tserve[client]"
    ```

Send the same request:

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
```

The input may also be a pandas, polars, or pyarrow table. See the [Python client](client/python.md) for type-preserving responses and the [data specification](client/data.md) for every request field and table format.

## Next

- [Choose another model](models/index.md)
- [Configure Docker](server/docker.md)
- [Understand the architecture](overview.md)
- [Explore HTTP](client/http.md) or the [Python client](client/python.md)
