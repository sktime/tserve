# Catalog

110 models a TServe process *can* load. The server always loads `naive`, a no-download baseline for testing. Name a catalog model as a leftover positional for a real forecast. `GET /models` reports what did. The same model goes in leftover [CLI](../reference/cli.md#flags) positionals and in a request's [`model`](../client/data.md#prediction-horizon-and-model) field.

## Dependencies

--8<-- "includes/model-dependencies.md"

## Start a server

=== "base"

    `naive` only — a test baseline, nothing downloaded. Full page: [base](base.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:base
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server]"
        uv run tserve
        ```

    === "pip"

        ```bash
        pip install "tserve[server]"
        tserve
        ```

=== "hub"

    Chronos Bolt, Chronos T5, TTM, TimesFM 2.x: 81 models, plus `naive`. Full page: [hub](hub.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,hub]"
        uv run tserve chronos_bolt
        ```

    === "pip"

        ```bash
        pip install "tserve[server,hub]"
        tserve chronos_bolt
        ```

=== "chronos"

    Chronos-2, plus every [hub](hub.md) model. Full page: [chronos](chronos.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:chronos chronos_2
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,chronos]"
        uv run tserve chronos_2
        ```

    === "pip"

        ```bash
        pip install "tserve[server,chronos]"
        tserve chronos_2
        ```

=== "kronos"

    Kronos and WindFM. Sits on `base`, so **no** Hub models. Full page: [kronos](kronos.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:kronos kronos
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,kronos]"
        uv run tserve kronos
        ```

    === "pip"

        ```bash
        pip install "tserve[server,kronos]"
        tserve kronos
        ```

=== "granite"

    FlowState, plus every [hub](hub.md) model. Full page: [granite](granite.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:granite flowstate
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,granite]"
        uv run tserve flowstate
        ```

    === "pip"

        ```bash
        pip install "tserve[server,granite]"
        tserve flowstate
        ```

=== "moirai"

    Moirai 2, Moirai 1.x, Lag-Llama, plus every [hub](hub.md) model. Full page: [moirai](moirai.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,moirai]"
        uv run tserve moirai_2
        ```

    === "pip"

        ```bash
        pip install "tserve[server,moirai]"
        tserve moirai_2
        ```

=== "tirex"

    TiRex, plus every [hub](hub.md) model. Full page: [tirex](tirex.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:tirex tirex
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,tirex]"
        uv run tserve tirex
        ```

    === "pip"

        ```bash
        pip install "tserve[server,tirex]"
        tserve tirex
        ```

=== "toto"

    Toto-2, plus every [hub](hub.md) model. Full page: [toto](toto.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:toto toto_2_0_4m
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,toto]"
        uv run tserve toto_2_0_4m
        ```

    === "pip"

        ```bash
        pip install "tserve[server,toto]"
        tserve toto_2_0_4m
        ```

=== "mantis"

    Mantis, plus every [hub](hub.md) model. Needs `past` longer than 127 rows. Full page: [mantis](mantis.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:mantis mantis_8m
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,mantis]"
        uv run tserve mantis_8m
        ```

    === "pip"

        ```bash
        pip install "tserve[server,mantis]"
        tserve mantis_8m
        ```

=== "full"

    All 110 models, and the only way to mix two family stacks. Full page: [full](full.md).

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 sktime/tserve:full \
          chronos_2 tirex kronos
        ```

    === "uv"

        ```bash
        uv pip install "tserve[server,full]"
        uv run tserve chronos_2 tirex kronos
        ```

    === "pip"

        ```bash
        pip install "tserve[server,full]"
        tserve chronos_2 tirex kronos
        ```

- Docker tags, token, and cache volume: [Docker](../server/docker.md). GPU: swap in the `-gpu` tag and add `--gpus all` ([GPU images](../server/docker.md#gpu-images)).
- `uv` and `pip` install from PyPI: [uv / pip](../server/pip.md#install). From a clone: [From source](../server/source.md#install).
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
      "model": "chronos_bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
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
            model="chronos_bolt",
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

## Capabilities

Every capability is read from the estimator, not set by a TServe flag. [Multivariate](../client/data.md#targets) is more than one `target`; [exogenous](../client/data.md#future-and-static-data) is a covariate the model actually uses instead of ignoring; [quantiles](../client/data.md#quantiles) are prediction intervals ([HTTP](../client/http.md#request-quantiles), [Python](../client/python.md#request-quantiles)).

| family | multivariate | exogenous | quantiles |
| --- | :-: | :-: | :-: |
| [Naive](#naive) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } |
| [Chronos-2](#chronos-2) | :material-check:{ .tserve-yes } | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } |
| [Chronos Bolt](#chronos-bolt) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } |
| [Chronos T5](#chronos-t5) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } |
| [TTM](#ttm) | :material-check:{ .tserve-yes } | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } |
| [TimesFM](#timesfm) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } |
| [Kronos](#kronos) | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } |
| [WindFM](#windfm) | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } | :material-check:{ .tserve-yes } |
| [FlowState](#flowstate) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } |
| [Moirai 2](#moirai-2) | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } |
| [Moirai 1.x](#moirai-1x) | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } |
| [Lag-Llama](#lag-llama) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } |
| [TiRex](#tirex) | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } |
| [Toto-2](#toto-2) | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } | :material-check:{ .tserve-yes } |
| [Mantis](#mantis) | :material-check:{ .tserve-yes } | :material-minus:{ .tserve-no } | :material-minus:{ .tserve-no } |

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
