# chronos

Chronos-2: multivariate, with covariates. Plus every [`hub`](hub.md) id.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `chronos` | [`:chronos`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos) | [`:chronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos-gpu) | Chronos-2 | 3 | `chronos-2` |

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra chronos
    uv run fomo serve --load-models chronos-2
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,chronos]"
    fomo serve --load-models chronos-2
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 geetu040/fomo:chronos --load-models chronos-2
    ```

GPU: swap in
[`:chronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos-gpu)
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
      "model": "chronos-2"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos-2"}'
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
            model="chronos-2",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/chronos-2.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM](hub.md#timesfm): 81 ids, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
