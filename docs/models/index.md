# Catalog

110 ids a FoMo process *can* load. The server always loads `naive`, a
no-download baseline for testing. Name a catalog id with
[`--model`](../reference/cli.md#flags) or leftover positionals for a real
forecast. `GET /models` reports what did. The same id goes in `--model` and in
a request's [`model`](../client/data.md#prediction-horizon-and-model) field.

## Dependencies

--8<-- "includes/model-dependencies.md"

## Start a server

=== "base"

    `naive` only — a test baseline, nothing downloaded. Full page: [base](base.md).

    === "uv"

        ```bash
        uv sync --extra server
        uv run fomo serve
        ```

    === "pip"

        ```bash
        pip install -e ".[server]"
        fomo serve
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:base
        ```

=== "hub"

    Chronos Bolt, Chronos T5, TTM, TimesFM 2.x: 81 ids, plus `naive`. Full
    page: [hub](hub.md).

    === "uv"

        ```bash
        uv sync --extra server --extra hub
        uv run fomo serve --model chronos-bolt
        ```

    === "pip"

        ```bash
        pip install -e ".[server,hub]"
        fomo serve --model chronos-bolt
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:hub --model chronos-bolt
        ```

=== "chronos"

    Chronos-2, plus every [hub](hub.md) id. Full page: [chronos](chronos.md).

    === "uv"

        ```bash
        uv sync --extra server --extra chronos
        uv run fomo serve --model chronos-2
        ```

    === "pip"

        ```bash
        pip install -e ".[server,chronos]"
        fomo serve --model chronos-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:chronos --model chronos-2
        ```

=== "kronos"

    Kronos and WindFM. Sits on `base`, so **no** Hub ids. Full page:
    [kronos](kronos.md).

    === "uv"

        ```bash
        uv sync --extra server --extra kronos
        uv run fomo serve --model kronos
        ```

    === "pip"

        ```bash
        pip install -e ".[server,kronos]"
        fomo serve --model kronos
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:kronos --model kronos
        ```

=== "granite"

    FlowState, plus every [hub](hub.md) id. Full page: [granite](granite.md).

    === "uv"

        ```bash
        uv sync --extra server --extra granite
        uv run fomo serve --model flowstate
        ```

    === "pip"

        ```bash
        pip install -e ".[server,granite]"
        fomo serve --model flowstate
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:granite --model flowstate
        ```

=== "moirai"

    Moirai 2, Moirai 1.x, Lag-Llama, plus every [hub](hub.md) id. Full page:
    [moirai](moirai.md).

    === "uv"

        ```bash
        uv sync --extra server --extra moirai
        uv run fomo serve --model moirai-2
        ```

    === "pip"

        ```bash
        pip install -e ".[server,moirai]"
        fomo serve --model moirai-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:moirai --model moirai-2
        ```

=== "tirex"

    TiRex, plus every [hub](hub.md) id. Full page: [tirex](tirex.md).

    === "uv"

        ```bash
        uv sync --extra server --extra tirex
        uv run fomo serve --model tirex
        ```

    === "pip"

        ```bash
        pip install -e ".[server,tirex]"
        fomo serve --model tirex
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:tirex --model tirex
        ```

=== "toto"

    Toto-2, plus every [hub](hub.md) id. Full page: [toto](toto.md).

    === "uv"

        ```bash
        uv sync --extra server --extra toto
        uv run fomo serve --model toto-2.0-4m
        ```

    === "pip"

        ```bash
        pip install -e ".[server,toto]"
        fomo serve --model toto-2.0-4m
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:toto --model toto-2.0-4m
        ```

=== "mantis"

    Mantis, plus every [hub](hub.md) id. Needs `past` longer than 127 rows.
    Full page: [mantis](mantis.md).

    === "uv"

        ```bash
        uv sync --extra server --extra mantis
        uv run fomo serve --model mantis-8m
        ```

    === "pip"

        ```bash
        pip install -e ".[server,mantis]"
        fomo serve --model mantis-8m
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:mantis --model mantis-8m
        ```

=== "full"

    All 110 ids, and the only way to mix two family stacks. Full page:
    [full](full.md).

    === "uv"

        ```bash
        uv sync --extra server --extra full
        uv run fomo serve --model chronos-2 tirex kronos
        ```

    === "pip"

        ```bash
        pip install -e ".[server,full]"
        fomo serve --model chronos-2 tirex kronos
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:full \
          --model chronos-2 tirex kronos
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
            model="chronos-bolt",
        )
    print(result.predictions)
    ```

Only `model` changes between extras. Python needs the
[`client`](../client/python.md#install) extra on the caller. Every field,
format, and response shape: [Data specification](../client/data.md).

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

Read from the estimator, not a FoMo flag. Ask for levels with the `quantiles`
field: [HTTP](../client/http.md#request-quantiles),
[Python](../client/python.md#request-quantiles).

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

    [:octicons-arrow-right-24: HTTP](../client/http.md) or
    [Python](../client/python.md)

-   :material-text:{ .lg .middle } **Beyond the catalog**

    ---

    Craft specs, live objects, and saved `.zip` models.

    [:octicons-arrow-right-24: Craft specs](../server/craft-specs.md)

</div>
