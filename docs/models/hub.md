# hub

Four Hugging Face families, 81 of the catalog's 110 models. The usual starting point.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `hub` | [`:hub`](https://hub.docker.com/r/sktime/tserve/tags?name=hub) | [`:hub-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=hub-gpu) | Chronos Bolt, Chronos T5, TTM, TimesFM 2.x | 81 | `chronos-bolt` |

Builds on [`base`](base.md), so `naive` is available here too. Every extra that pulls `hf` builds on `hub`, so those pages can load these models as well.

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    uv sync --extra server --extra hub
    uv run tserve chronos-bolt
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    pip install -e ".[server,hub]"
    tserve chronos-bolt
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:hub chronos-bolt
    ```

GPU: swap in [`:hub-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=hub-gpu) and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).

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
      "model": "chronos-bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos-bolt"}'
    ```

=== "Python"

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
            model="chronos-bolt",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/chronos-bolt.md"

--8<-- "includes/models/chronos-t5.md"

--8<-- "includes/models/ttm.md"

--8<-- "includes/models/timesfm.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).

## Next steps

--8<-- "includes/models/next-steps.md"
