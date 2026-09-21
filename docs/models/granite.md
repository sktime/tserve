# granite

IBM FlowState, plus every [`hub`](hub.md) model.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `granite` | [`:granite`](https://hub.docker.com/r/geetu040/tserve/tags?name=granite) | [`:granite-gpu`](https://hub.docker.com/r/geetu040/tserve/tags?name=granite-gpu) | FlowState | 2 | `flowstate` |

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    uv sync --extra server --extra granite
    uv run tserve serve --model flowstate
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    pip install -e ".[server,granite]"
    tserve serve --model flowstate
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 geetu040/tserve:granite --model flowstate
    ```

GPU: swap in
[`:granite-gpu`](https://hub.docker.com/r/geetu040/tserve/tags?name=granite-gpu)
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
      "model": "flowstate"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"flowstate"}'
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
            model="flowstate",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/flowstate.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM](hub.md#timesfm): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
