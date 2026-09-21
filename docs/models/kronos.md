# kronos

Kronos and WindFM.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `kronos` | [`:kronos`](https://hub.docker.com/r/sktime/tserve/tags?name=kronos) | [`:kronos-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=kronos-gpu) | Kronos, WindFM | 5 | `kronos` |

Builds on [`base`](base.md), **not** [`hub`](hub.md): no Chronos Bolt, Chronos T5, TTM, or TimesFM here. To mix, use [`full`](full.md).

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    uv sync --extra server --extra kronos
    uv run tserve serve kronos
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    pip install -e ".[server,kronos]"
    tserve serve kronos
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:kronos kronos
    ```

GPU: swap in [`:kronos-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=kronos-gpu) and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).

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
      "model": "kronos"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"kronos"}'
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
            model="kronos",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/kronos.md"

--8<-- "includes/models/windfm.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).

## Next steps

--8<-- "includes/models/next-steps.md"
