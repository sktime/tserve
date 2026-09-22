# toto

Datadog Toto-2, 4M to 2.5B parameters, plus every [`hub`](hub.md) model.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `toto` | [`:toto`](https://hub.docker.com/r/sktime/tserve/tags?name=toto) | [`:toto-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=toto-gpu) | Toto-2 | 5 | `toto_2_0_4m` |

## Start a server

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:toto toto_2_0_4m
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,toto]"
    ```

    ```bash
    uv run tserve toto_2_0_4m
    ```

=== "pip"

    ```bash
    pip install "tserve[server,toto]"
    ```

    ```bash
    tserve toto_2_0_4m
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
      "model": "toto_2_0_4m"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"toto_2_0_4m"}'
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
            model="toto_2_0_4m",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/toto.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM 2.x](hub.md#timesfm-2x): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
