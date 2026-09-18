# base

The `naive` baseline and nothing else. Downloads no weights.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `server` | [`:base`](https://hub.docker.com/r/geetu040/fomo/tags?name=base) | none | Naive | 1 | `naive` |

Every other page in this section layers on top of this one.

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server
    uv run fomo serve --load-models naive
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server]"
    fomo serve --load-models naive
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 geetu040/fomo:base --load-models naive
    ```

There is no `:base-gpu` image.

Check what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

## Predict

Python needs the [`client`](../client/python.md#install) extra on the caller.

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
      "model": "naive"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"naive"}'
    ```

=== "Python"

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
            model="naive",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/naive.md"

## Also loadable here

Nothing. `:base` carries no Hugging Face stack, so any other id fails at
startup ([Errors](../reference/errors.md#startup)). For Chronos Bolt, Chronos
T5, TTM, and TimesFM, use [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
