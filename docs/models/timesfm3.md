# timesfm3

Google TimesFM 3, plus every [`hub`](hub.md) model.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `timesfm3` | [`:timesfm3`](https://hub.docker.com/r/sktime/tserve/tags?name=timesfm3) | [`:timesfm3-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=timesfm3-gpu) | TimesFM 3 | 1 | `timesfm_3` |

!!! note "License"

    The registry crafts TimesFM 3 with `license_accepted=True`. Weights use the [TimesFM non-commercial license](https://huggingface.co/google/timesfm-3.0-pytorch/blob/main/LICENSE).

## Start a server

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:timesfm3 timesfm_3
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,timesfm3]"
    ```

    ```bash
    uv run tserve timesfm_3
    ```

=== "pip"

    ```bash
    pip install "tserve[server,timesfm3]"
    ```

    ```bash
    tserve timesfm_3
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
      "model": "timesfm_3"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"timesfm_3"}'
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
            model="timesfm_3",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/timesfm-3.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM 2.x](hub.md#timesfm-2x): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
