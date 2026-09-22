# mantis

Mantis embeddings with an sklearn head, plus every [`hub`](hub.md) model.

| extra | CPU tag | GPU tag | families | models | example |
| --- | --- | --- | --- | --- | --- |
| `mantis` | [`:mantis`](https://hub.docker.com/r/sktime/tserve/tags?name=mantis) | [`:mantis-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=mantis-gpu) | Mantis | 3 | `mantis_8m` |

!!! warning "`past` needs more than 127 rows"

    `context_length` is 127. The examples below send 150 rows; the five-row series used on other pages fails here.

## Start a server

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:mantis mantis_8m
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,mantis]"
    ```

    ```bash
    uv run tserve mantis_8m
    ```

=== "pip"

    ```bash
    pip install "tserve[server,mantis]"
    ```

    ```bash
    tserve mantis_8m
    ```

GPU: swap in [`:mantis-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=mantis-gpu) and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).

Check what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

## Predict

150 rows of history, because `context_length` is 127. Python needs the [`client`](../client/python.md#install) extra on the caller.

=== "bash / zsh"

    ```bash
    python - <<'PY'
    import datetime, json

    start = datetime.date(2024, 1, 1)
    past = {
        "timestamp": [(start + datetime.timedelta(days=i)).isoformat() for i in range(150)],
        "sales": [120 + (i % 7) * 3 for i in range(150)],
    }
    payload = {"past": past, "time": "timestamp", "target": ["sales"], "fh": 3,
               "model": "mantis_8m"}
    json.dump(payload, open("mantis.json", "w"))
    PY

    curl -s http://127.0.0.1:8000/predict \
      -H "Content-Type: application/json" -d @mantis.json
    ```

=== "PowerShell"

    Save the Python from the other tab as `make_payload.py`, then:

    ```powershell
    python make_payload.py
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "@mantis.json"
    ```

=== "Python"

    ```python
    import datetime

    from tserve.client import Client

    start = datetime.date(2024, 1, 1)
    past = {
        "timestamp": [(start + datetime.timedelta(days=i)).isoformat() for i in range(150)],
        "sales": [120 + (i % 7) * 3 for i in range(150)],
    }

    with Client("http://127.0.0.1:8000") as client:
        result = client.predict(
            past=past,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="mantis_8m",
        )
    print(result.predictions)
    ```

## Models

--8<-- "includes/models/mantis.md"

## Also loadable here

- [Naive](base.md#naive): `naive`, from [`base`](base.md).
- [Chronos Bolt](hub.md#chronos-bolt), [Chronos T5](hub.md#chronos-t5), [TTM](hub.md#ttm), [TimesFM](hub.md#timesfm): 81 models, from [`hub`](hub.md).

## Next steps

--8<-- "includes/models/next-steps.md"
