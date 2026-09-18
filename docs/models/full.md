# full

Every family in one extra. Use it when your ids span more than one family
extra.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `full` | [`:full`](https://hub.docker.com/r/geetu040/fomo/tags?name=full) | [`:full-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=full-gpu) | all of them | 110 | `chronos-2` |

`chronos` + `kronos` + `granite` + `moirai` + `tirex` + `toto` + `mantis`,
which pulls in `hub` and `base`. It is also the largest install: for one
family, the extra on that family's page pulls far less.

## Start a server

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra full
    uv run fomo serve --load-models chronos-2 tirex kronos
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,full]"
    fomo serve --load-models chronos-2 tirex kronos
    ```

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 geetu040/fomo:full \
      --load-models chronos-2 tirex kronos
    ```

GPU: swap in
[`:full-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=full-gpu) and
add `--gpus all` ([GPU images](../server/docker.md#gpu-images)). Each id costs
a download at first start and stays in memory.

Check what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

## Predict

One process answers for every loaded id; switch by changing `model`. Python
needs the [`client`](../client/python.md#install) extra on the caller.

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
        for model in ("chronos-2", "tirex", "kronos"):
            result = client.predict(
                past=past,
                time="timestamp",
                target=["sales"],
                fh=3,
                model=model,
            )
            print(model, result.predictions)
    ```

## Models

All 110 ids load here. Checkpoints for all of them:
[All models](index.md#all-models).

| extra | families | models | ids |
| --- | --- | --- | --- |
| `server` | Naive | 1 | [base](base.md#models) |
| `hub` | Chronos Bolt, Chronos T5, TTM, TimesFM 2.x | 81 | [hub](hub.md#models) |
| `chronos` | Chronos-2 | 3 | [chronos](chronos.md#models) |
| `kronos` | Kronos, WindFM | 5 | [kronos](kronos.md#models) |
| `granite` | FlowState | 2 | [granite](granite.md#models) |
| `moirai` | Moirai 2, Moirai 1.x, Lag-Llama | 8 | [moirai](moirai.md#models) |
| `tirex` | TiRex | 2 | [tirex](tirex.md#models) |
| `toto` | Toto-2 | 5 | [toto](toto.md#models) |
| `mantis` | Mantis | 3 | [mantis](mantis.md#models) |

## Also loadable here

Combinations no single family extra allows. `kronos` alone cannot load a TTM
id, `tirex` alone cannot load a Kronos id; `full` serves all three at once:

```bash
fomo serve --load-models kronos ttm-r3 tirex
```

## Next steps

--8<-- "includes/models/next-steps.md"
