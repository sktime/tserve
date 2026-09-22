# chronos

Chronos-2: multivariate, with covariates. Plus every [`hub`](hub.md) model.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `chronos` | [`:chronos`](https://hub.docker.com/r/sktime/tserve/tags?name=chronos) | [`:chronos-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=chronos-gpu) | Chronos-2 | 3 | `chronos_2` |

## Start a server

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:chronos chronos_2
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,chronos]"
    ```

    ```bash
    uv run tserve chronos_2
    ```

=== "pip"

    ```bash
    pip install "tserve[server,chronos]"
    ```

    ```bash
    tserve chronos_2
    ```

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
      "model": "chronos_2"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_2"}'
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
            model="chronos_2",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/chronos-2.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM](hub.md#timesfm): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
