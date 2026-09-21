# Catalog

110 models a TServe process *can* load. The server always loads `naive`, a no-download baseline for testing. Name a catalog model as a leftover positional for a real forecast. `GET /models` reports what did. The same model goes in leftover [CLI](../reference/cli.md#flags) positionals and in a request's [`model`](../client/data.md#prediction-horizon-and-model) field.

## Dependencies

--8<-- "includes/model-dependencies.md"

## Start a server

=== "base"

    `naive` only — a test baseline, nothing downloaded. Full page: [base](base.md).

    === "uv"

        ```bash
        uv sync --extra server
        uv run tserve
        ```

    === "pip"

        ```bash
        pip install -e ".[server]"
        tserve
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:base
        ```

=== "hub"

    Chronos Bolt, Chronos T5, TTM, TimesFM 2.x: 81 models, plus `naive`. Full page: [hub](hub.md).

    === "uv"

        ```bash
        uv sync --extra server --extra hub
        uv run tserve chronos-bolt
        ```

    === "pip"

        ```bash
        pip install -e ".[server,hub]"
        tserve chronos-bolt
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:hub chronos-bolt
        ```

=== "chronos"

    Chronos-2, plus every [hub](hub.md) model. Full page: [chronos](chronos.md).

    === "uv"

        ```bash
        uv sync --extra server --extra chronos
        uv run tserve chronos-2
        ```

    === "pip"

        ```bash
        pip install -e ".[server,chronos]"
        tserve chronos-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:chronos chronos-2
        ```

=== "kronos"

    Kronos and WindFM. Sits on `base`, so **no** Hub models. Full page: [kronos](kronos.md).

    === "uv"

        ```bash
        uv sync --extra server --extra kronos
        uv run tserve kronos
        ```

    === "pip"

        ```bash
        pip install -e ".[server,kronos]"
        tserve kronos
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:kronos kronos
        ```

=== "granite"

    FlowState, plus every [hub](hub.md) model. Full page: [granite](granite.md).

    === "uv"

        ```bash
        uv sync --extra server --extra granite
        uv run tserve flowstate
        ```

    === "pip"

        ```bash
        pip install -e ".[server,granite]"
        tserve flowstate
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:granite flowstate
        ```

=== "moirai"

    Moirai 2, Moirai 1.x, Lag-Llama, plus every [hub](hub.md) model. Full page: [moirai](moirai.md).

    === "uv"

        ```bash
        uv sync --extra server --extra moirai
        uv run tserve moirai-2
        ```

    === "pip"

        ```bash
        pip install -e ".[server,moirai]"
        tserve moirai-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:moirai moirai-2
        ```

=== "tirex"

    TiRex, plus every [hub](hub.md) model. Full page: [tirex](tirex.md).

    === "uv"

        ```bash
        uv sync --extra server --extra tirex
        uv run tserve tirex
        ```

    === "pip"

        ```bash
        pip install -e ".[server,tirex]"
        tserve tirex
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:tirex tirex
        ```

=== "toto"

    Toto-2, plus every [hub](hub.md) model. Full page: [toto](toto.md).

    === "uv"

        ```bash
        uv sync --extra server --extra toto
        uv run tserve toto-2.0-4m
        ```

    === "pip"

        ```bash
        pip install -e ".[server,toto]"
        tserve toto-2.0-4m
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:toto toto-2.0-4m
        ```

=== "mantis"

    Mantis, plus every [hub](hub.md) model. Needs `past` longer than 127 rows. Full page: [mantis](mantis.md).

    === "uv"

        ```bash
        uv sync --extra server --extra mantis
        uv run tserve mantis-8m
        ```

    === "pip"

        ```bash
        pip install -e ".[server,mantis]"
        tserve mantis-8m
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:mantis mantis-8m
        ```

=== "full"

    All 110 models, and the only way to mix two family stacks. Full page: [full](full.md).

    === "uv"

        ```bash
        uv sync --extra server --extra full
        uv run tserve chronos-2 tirex kronos
        ```

    === "pip"

        ```bash
        pip install -e ".[server,full]"
        tserve chronos-2 tirex kronos
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:full \
          chronos-2 tirex kronos
        ```

- `uv` and `pip` assume a clone: [From source](../server/source.md#install).
- GPU: swap in the `-gpu` tag and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).
- Token and cache volume: [Docker](../server/docker.md).
- Ids not listed here: [craft specs](../server/craft-specs.md), [live objects](../server/live-objects.md), [a directory of `.zip` files](../server/models-dir.md).

## Predict

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
      "model": "chronos-bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos-bolt"}'
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
            model="chronos-bolt",
        )
    print(result.predictions)
    ```

Only `model` changes between extras. Python needs the [`client`](../client/python.md#install) extra on the caller. Every field, format, and response shape: [Data specification](../client/data.md).

## All models

--8<-- "includes/models/naive.md"

--8<-- "includes/models/chronos-bolt.md"

--8<-- "includes/models/chronos-t5.md"

--8<-- "includes/models/ttm.md"

--8<-- "includes/models/timesfm.md"

--8<-- "includes/models/chronos-2.md"

--8<-- "includes/models/kronos.md"

--8<-- "includes/models/windfm.md"

--8<-- "includes/models/flowstate.md"

--8<-- "includes/models/moirai-2.md"

--8<-- "includes/models/moirai-1x.md"

--8<-- "includes/models/lagllama.md"

--8<-- "includes/models/tirex.md"

--8<-- "includes/models/toto.md"

--8<-- "includes/models/mantis.md"

## Quantile support

Read from the estimator, not a TServe flag. Ask for levels with the `quantiles` field: [HTTP](../client/http.md#request-quantiles), [Python](../client/python.md#request-quantiles).

| | families |
| --- | --- |
| Returns quantiles | [Naive](#naive), [TimesFM](#timesfm), [WindFM](#windfm), [Lag-Llama](#lag-llama), [FlowState](#flowstate), [Toto-2](#toto-2) |
| Point forecasts only | [Chronos-2](#chronos-2), [Chronos Bolt](#chronos-bolt), [Chronos T5](#chronos-t5), [TTM](#ttm), [Kronos](#kronos), [Moirai 2](#moirai-2), [Moirai 1.x](#moirai-1x), [TiRex](#tirex), [Mantis](#mantis) |

## Where to next

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } **Run a server**

    ---

    Flags, `Server`, `server.app`, and the process lifecycle.

    [:octicons-arrow-right-24: Server](../server/index.md)

-   :material-docker:{ .lg .middle } **Docker**

    ---

    Tags, Hugging Face token, cache volume, GPU, and building images.

    [:octicons-arrow-right-24: Docker](../server/docker.md)

-   :material-api:{ .lg .middle } **Send predictions**

    ---

    JSON over `POST /predict`, or native tables from Python.

    [:octicons-arrow-right-24: HTTP](../client/http.md) or [Python](../client/python.md)

-   :material-text:{ .lg .middle } **Beyond the catalog**

    ---

    Craft specs, live objects, and saved `.zip` models.

    [:octicons-arrow-right-24: Craft specs](../server/craft-specs.md)

</div>
