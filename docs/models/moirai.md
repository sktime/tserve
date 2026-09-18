# moirai

Moirai 2, Moirai 1.x, and Lag-Llama, plus every [`hub`](hub.md) id.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `moirai` | [`:moirai`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai) | [`:moirai-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai-gpu) | Moirai 2, Moirai 1.x, Lag-Llama | 8 | `moirai-2` |

!!! note "Python pins"

    `gluonts`, `lightning`, and `hydra-core` are pinned only for
    `python_version < '3.14'`.

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra moirai
    uv run fomo serve --model moirai-2
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,moirai]"
    fomo serve --model moirai-2
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 geetu040/fomo:moirai --model moirai-2
    ```

GPU: swap in
[`:moirai-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai-gpu)
and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).

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
      "model": "moirai-2"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"moirai-2"}'
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
            model="moirai-2",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/moirai-2.md"

--8<-- "includes/models/moirai-1x.md"

--8<-- "includes/models/lagllama.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM](hub.md#timesfm): 81 ids, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
