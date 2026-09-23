# tirex2

NX-AI TiRex-2, plus every [`hub`](hub.md) model. TiRex v1 stays on [`tirex`](tirex.md).

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `tirex2` | [`:tirex2`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex2) | [`:tirex2-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex2-gpu) | TiRex-2 | 4 | `tirex_2` |

!!! note "Gated checkpoints"

    `tirex_2` is public. `tirex_2_gifteval_zs`, `tirex_2_gifteval_pretrain`, and `tirex_2_fevbench` are gated. Accept the model card and set a [Hugging Face token](../server/docker.md#hugging-face-token) before loading those three.

## Start a server

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:tirex2 tirex_2
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,tirex2]"
    ```

    ```bash
    uv run tserve tirex_2
    ```

=== "pip"

    ```bash
    pip install "tserve[server,tirex2]"
    ```

    ```bash
    tserve tirex_2
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
      "model": "tirex_2"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"tirex_2"}'
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
            model="tirex_2",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/tirex-2.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM 2.x](hub.md#timesfm-2x): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
