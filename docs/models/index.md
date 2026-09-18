# Catalog

FoMo ships **110 supported models**, pre-registered and ready to serve under the names below. That is the list this process *can* load. Nothing is loaded until `--load-models` / `load_models` names it. `GET /models` is the loaded list, not this page. How to start a process is on [Server](../server/index.md).

The name in the `model` column is what you pass to `--load-models` and to a predict request. `naive` needs no Hub download; every other model fetches a checkpoint on first load.

Pick a tab for the extra / image you want. Each one has source (`uv` / `pip`) and Docker commands, HTTP and Python predict snippets, and the model ids that extra can load. Token, cache, and GPU details: [Docker](../server/docker.md). Clone installs: [From source](../server/source.md#dependencies).

=== "base"

    Naive only. Extra `server`. Image [`:base`](https://hub.docker.com/r/geetu040/fomo/tags?name=base). There is no `:base-gpu`.

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server
        uv run fomo serve --load-models naive
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server]"
        fomo serve --load-models naive
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:base --load-models naive
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

        ```bash
        curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
          "past": {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "sales": [120, 135, 128, 142, 138]
          },
          "time": "timestamp",
          "target": ["sales"],
          "fh": 3,
          "model": "naive"
        }'
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
                model="naive",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Naive | `naive` |

=== "hub"

    Chronos Bolt, Chronos T5, TTM, TimesFM 2.x, and `naive`. Extra `hub`. Images [`:hub`](https://hub.docker.com/r/geetu040/fomo/tags?name=hub) / [`:hub-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=hub-gpu). The same models also load on any extra that pulls `hf` (`chronos`, `granite`, `moirai`, `tirex`, `toto`, `mantis`, `full`).

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra hub
        uv run fomo serve --load-models chronos-bolt
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,hub]"
        fomo serve --load-models chronos-bolt
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:hub-gpu --load-models chronos-bolt
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

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

    **Models**

    | family | ids |
    | --- | --- |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "chronos"

    Chronos-2, plus every Hub model. Extra `chronos`. Images [`:chronos`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos) / [`:chronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos-gpu).

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra chronos
        uv run fomo serve --load-models chronos-2
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,chronos]"
        fomo serve --load-models chronos-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:chronos --load-models chronos-2
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:chronos-gpu --load-models chronos-2
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

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
                model="chronos-2",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Chronos-2 | `chronos-2`, `chronos-2-small`, `chronos-2-synth` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "kronos"

    Kronos and WindFM, plus `naive`. Extra `kronos`. Images [`:kronos`](https://hub.docker.com/r/geetu040/fomo/tags?name=kronos) / [`:kronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=kronos-gpu). This image sits on `base`, not `hub`, so it cannot load Chronos Bolt, TTM, or TimesFM.

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra kronos
        uv run fomo serve --load-models kronos
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,kronos]"
        fomo serve --load-models kronos
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:kronos --load-models kronos
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:kronos-gpu --load-models kronos
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

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
                model="kronos",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Naive | `naive` |
    | Kronos | `kronos`, `kronos-mini`, `kronos-base` |
    | WindFM | `windfm`, `windfm-robust` |

=== "granite"

    FlowState, plus every Hub model. Extra `granite`. Images [`:granite`](https://hub.docker.com/r/geetu040/fomo/tags?name=granite) / [`:granite-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=granite-gpu).

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra granite
        uv run fomo serve --load-models flowstate
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,granite]"
        fomo serve --load-models flowstate
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:granite --load-models flowstate
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:granite-gpu --load-models flowstate
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

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
                model="flowstate",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | FlowState | `flowstate`, `flowstate-granite` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "moirai"

    Moirai 2, Moirai 1.x, Lag-Llama, plus every Hub model. Extra `moirai`. Images [`:moirai`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai) / [`:moirai-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai-gpu).

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra moirai
        uv run fomo serve --load-models moirai-2
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,moirai]"
        fomo serve --load-models moirai-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:moirai --load-models moirai-2
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:moirai-gpu --load-models moirai-2
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

        ```bash
        curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
          "past": {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "sales": [120, 135, 128, 142, 138]
          },
          "time": "timestamp",
          "target": ["sales"],
          "fh": 3,
          "model": "moirai-2"
        }'
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
                model="moirai-2",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Moirai 2 | `moirai-2` |
    | Moirai 1.x | `moirai-1.0-r-small`, `moirai-1.0-r-base`, `moirai-1.0-r-large`, `moirai-1.1-r-small`, `moirai-1.1-r-base`, `moirai-1.1-r-large` |
    | Lag-Llama | `lagllama` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "tirex"

    TiRex, plus every Hub model. Extra `tirex`. Images [`:tirex`](https://hub.docker.com/r/geetu040/fomo/tags?name=tirex) / [`:tirex-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=tirex-gpu). The registry sets `license_accepted=True`.

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra tirex
        uv run fomo serve --load-models tirex
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,tirex]"
        fomo serve --load-models tirex
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:tirex --load-models tirex
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:tirex-gpu --load-models tirex
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

        ```bash
        curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
          "past": {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "sales": [120, 135, 128, 142, 138]
          },
          "time": "timestamp",
          "target": ["sales"],
          "fh": 3,
          "model": "tirex"
        }'
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
                model="tirex",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | TiRex | `tirex`, `tirex-1.1-gifteval` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "toto"

    Toto-2, plus every Hub model. Extra `toto`. Images [`:toto`](https://hub.docker.com/r/geetu040/fomo/tags?name=toto) / [`:toto-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=toto-gpu).

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra toto
        uv run fomo serve --load-models toto-2.0-4m
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,toto]"
        fomo serve --load-models toto-2.0-4m
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:toto --load-models toto-2.0-4m
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:toto-gpu --load-models toto-2.0-4m
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

        ```bash
        curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
          "past": {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "sales": [120, 135, 128, 142, 138]
          },
          "time": "timestamp",
          "target": ["sales"],
          "fh": 3,
          "model": "toto-2.0-4m"
        }'
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
                model="toto-2.0-4m",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Toto-2 | `toto-2.0-4m`, `toto-2.0-22m`, `toto-2.0-313m`, `toto-2.0-1b`, `toto-2.0-2.5b` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "mantis"

    Mantis, plus every Hub model. Extra `mantis`. Images [`:mantis`](https://hub.docker.com/r/geetu040/fomo/tags?name=mantis) / [`:mantis-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=mantis-gpu). `context_length` is 127; history must be longer than that.

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra mantis
        uv run fomo serve --load-models mantis
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,mantis]"
        fomo serve --load-models mantis
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:mantis --load-models mantis
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:mantis-gpu --load-models mantis
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

        ```bash
        curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
          "past": {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "sales": [120, 135, 128, 142, 138]
          },
          "time": "timestamp",
          "target": ["sales"],
          "fh": 3,
          "model": "mantis"
        }'
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
                model="mantis",
            )
        print(result.predictions)
        ```

    **Models**

    | family | ids |
    | --- | --- |
    | Mantis | `mantis`, `mantis-8m`, `mantis-plus` |
    | Naive | `naive` |
    | Chronos Bolt | `chronos-bolt`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` |
    | Chronos T5 | `chronos-t5`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` |
    | TimesFM | `timesfm-2.5`, `timesfm-2` |
    | TTM | `ttm`, `ttm-r1`, `ttm-r2`, `ttm-r3`, and the revision ids under [TTM](#ttm) |

=== "full"

    Every family on this page. Extra `full`. Images [`:full`](https://hub.docker.com/r/geetu040/fomo/tags?name=full) / [`:full-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=full-gpu). Use this when the ids span more than one family extra.

    **Start the server**

    === "uv"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        uv sync --extra server --extra full
        uv run fomo serve --load-models chronos-2
        ```

    === "pip"

        ```bash
        git clone https://github.com/sktime/fomo.git && cd fomo
        pip install -e ".[server,full]"
        fomo serve --load-models chronos-2
        ```

    === "Docker"

        ```bash
        docker run --rm -p 8000:8000 geetu040/fomo:full --load-models chronos-2
        ```

        GPU:

        ```bash
        docker run --rm --gpus all -p 8000:8000 geetu040/fomo:full-gpu --load-models chronos-2
        ```

    **Predict** — Python needs the [`client`](../client/python.md) extra on the caller.

    === "HTTP"

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
                model="chronos-2",
            )
        print(result.predictions)
        ```

    **Models**

    All **110** ids below. Mix families in `--load-models`, for example `chronos-2 tirex`.

## Dependencies

--8<-- "includes/model-dependencies.md"

Install extras from a clone on [From source](../server/source.md#dependencies). Image tags, token, and cache: [Docker](../server/docker.md).

## Baseline

`NaiveForecaster`. Extra `server`, image [`:base`](https://hub.docker.com/r/geetu040/fomo/tags?name=base). Drift strategy, no weights.

| model | checkpoint |
| --- | --- |
| `naive` | — |

## Chronos-2

`Chronos2Forecaster`. Extra `chronos`, images [`:chronos`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos) / [`:chronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=chronos-gpu).

| model | checkpoint |
| --- | --- |
| `chronos-2` | [amazon/chronos-2](https://huggingface.co/amazon/chronos-2) |
| `chronos-2-small` | [autogluon/chronos-2-small](https://huggingface.co/autogluon/chronos-2-small) |
| `chronos-2-synth` | [autogluon/chronos-2-synth](https://huggingface.co/autogluon/chronos-2-synth) |

## Chronos Bolt

`ChronosForecaster`. Extra `hub`, images [`:hub`](https://hub.docker.com/r/geetu040/fomo/tags?name=hub) / [`:hub-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=hub-gpu). Does not support quantile prediction.

| model | checkpoint |
| --- | --- |
| `chronos-bolt` | [amazon/chronos-bolt-tiny](https://huggingface.co/amazon/chronos-bolt-tiny) |
| `chronos-bolt-mini` | [amazon/chronos-bolt-mini](https://huggingface.co/amazon/chronos-bolt-mini) |
| `chronos-bolt-small` | [amazon/chronos-bolt-small](https://huggingface.co/amazon/chronos-bolt-small) |
| `chronos-bolt-base` | [amazon/chronos-bolt-base](https://huggingface.co/amazon/chronos-bolt-base) |

## Chronos T5

`ChronosForecaster`. Same extra and images as Chronos Bolt. Does not support
quantile prediction.

| model | checkpoint |
| --- | --- |
| `chronos-t5` | [amazon/chronos-t5-tiny](https://huggingface.co/amazon/chronos-t5-tiny) |
| `chronos-t5-mini` | [amazon/chronos-t5-mini](https://huggingface.co/amazon/chronos-t5-mini) |
| `chronos-t5-small` | [amazon/chronos-t5-small](https://huggingface.co/amazon/chronos-t5-small) |
| `chronos-t5-base` | [amazon/chronos-t5-base](https://huggingface.co/amazon/chronos-t5-base) |
| `chronos-t5-large` | [amazon/chronos-t5-large](https://huggingface.co/amazon/chronos-t5-large) |

## TTM

`TinyTimeMixerForecaster`. Extra `hub`. Every id below pins a Hub repo and a
revision, named `{revision}-{context}-{horizon}` with optional `-lite` or
`-l1` — except the four short ids, which leave the revision (and for `ttm`
also the repo) at the forecaster default, so the context and horizon are
whatever that default branch ships.

### defaults

| model | repo | revision |
| --- | --- | --- |
| `ttm` | forecaster default (`ibm/TTM`) | forecaster default (`main`) |
| `ttm-r1` | [ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1) | forecaster default (`main`) |
| `ttm-r2` | [ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2) | forecaster default (`main`) |
| `ttm-r3` | [ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | forecaster default (`main`) |

### r1

[ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1)

| model | context | horizon |
| --- | --- | --- |
| `ttm-r1-512-96` | 512 | 96 |
| `ttm-r1-1024-96` | 1024 | 96 |

### r2

[ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2)

| model | context | horizon |
| --- | --- | --- |
| `ttm-r2-512-96` | 512 | 96 |
| `ttm-r2-512-192` | 512 | 192 |
| `ttm-r2-512-336` | 512 | 336 |
| `ttm-r2-512-720` | 512 | 720 |
| `ttm-r2-1024-96` | 1024 | 96 |
| `ttm-r2-1024-192` | 1024 | 192 |
| `ttm-r2-1024-336` | 1024 | 336 |
| `ttm-r2-1024-720` | 1024 | 720 |
| `ttm-r2-1536-96` | 1536 | 96 |
| `ttm-r2-1536-192` | 1536 | 192 |
| `ttm-r2-1536-336` | 1536 | 336 |
| `ttm-r2-1536-720` | 1536 | 720 |

### r2.1

Same Hub repo as r2. `-l1` is the L1 checkpoint.

| model | context | horizon | variant |
| --- | --- | --- | --- |
| `ttm-r2.1-52-16` | 52 | 16 | |
| `ttm-r2.1-52-16-l1` | 52 | 16 | L1 |
| `ttm-r2.1-90-30` | 90 | 30 | |
| `ttm-r2.1-90-30-l1` | 90 | 30 | L1 |
| `ttm-r2.1-180-60-l1` | 180 | 60 | L1 |
| `ttm-r2.1-360-60-l1` | 360 | 60 | L1 |
| `ttm-r2.1-512-48` | 512 | 48 | |
| `ttm-r2.1-512-48-l1` | 512 | 48 | L1 |
| `ttm-r2.1-512-96` | 512 | 96 | |
| `ttm-r2.1-512-96-l1` | 512 | 96 | L1 |

### r3

[ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3). Each model has a `-lite` sibling.

| model | lite | context | horizon |
| --- | --- | --- | --- |
| `ttm-r3-52-16` | `ttm-r3-52-16-lite` | 52 | 16 |
| `ttm-r3-90-30` | `ttm-r3-90-30-lite` | 90 | 30 |
| `ttm-r3-156-16` | `ttm-r3-156-16-lite` | 156 | 16 |
| `ttm-r3-180-60` | `ttm-r3-180-60-lite` | 180 | 60 |
| `ttm-r3-360-60` | `ttm-r3-360-60-lite` | 360 | 60 |
| `ttm-r3-512-30` | `ttm-r3-512-30-lite` | 512 | 30 |
| `ttm-r3-512-48` | `ttm-r3-512-48-lite` | 512 | 48 |
| `ttm-r3-512-96` | `ttm-r3-512-96-lite` | 512 | 96 |
| `ttm-r3-512-336` | `ttm-r3-512-336-lite` | 512 | 336 |
| `ttm-r3-768-48` | `ttm-r3-768-48-lite` | 768 | 48 |
| `ttm-r3-1024-48` | `ttm-r3-1024-48-lite` | 1024 | 48 |
| `ttm-r3-1024-96` | `ttm-r3-1024-96-lite` | 1024 | 96 |
| `ttm-r3-1024-720` | `ttm-r3-1024-720-lite` | 1024 | 720 |
| `ttm-r3-1536-96` | `ttm-r3-1536-96-lite` | 1536 | 96 |
| `ttm-r3-1536-720` | `ttm-r3-1536-720-lite` | 1536 | 720 |
| `ttm-r3-2048-96` | `ttm-r3-2048-96-lite` | 2048 | 96 |
| `ttm-r3-2048-720` | `ttm-r3-2048-720-lite` | 2048 | 720 |
| `ttm-r3-2560-96` | `ttm-r3-2560-96-lite` | 2560 | 96 |
| `ttm-r3-2560-720` | `ttm-r3-2560-720-lite` | 2560 | 720 |
| `ttm-r3-3072-96` | `ttm-r3-3072-96-lite` | 3072 | 96 |
| `ttm-r3-3072-720` | `ttm-r3-3072-720-lite` | 3072 | 720 |

## TimesFM

`TimesFM2Forecaster`. Extra `hub`. Supports quantile prediction for levels
available in the checkpoint configuration.

| model | checkpoint |
| --- | --- |
| `timesfm-2.5` | [google/timesfm-2.5-200m-transformers](https://huggingface.co/google/timesfm-2.5-200m-transformers) |
| `timesfm-2` | [google/timesfm-2.0-500m-pytorch](https://huggingface.co/google/timesfm-2.0-500m-pytorch) |

## Kronos

`KronosForecaster`. Extra `kronos`, images [`:kronos`](https://hub.docker.com/r/geetu040/fomo/tags?name=kronos) / [`:kronos-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=kronos-gpu). The tokenizer is part of the model, not a separate entry.

| model | checkpoint |
| --- | --- |
| `kronos` | [NeoQuasar/Kronos-small](https://huggingface.co/NeoQuasar/Kronos-small) |
| `kronos-mini` | [NeoQuasar/Kronos-mini](https://huggingface.co/NeoQuasar/Kronos-mini) |
| `kronos-base` | [NeoQuasar/Kronos-base](https://huggingface.co/NeoQuasar/Kronos-base) |

## WindFM

`WindFMForecaster`. Same extra and images as Kronos.

| model | checkpoint |
| --- | --- |
| `windfm` | [NeoQuasar/WindFM](https://huggingface.co/NeoQuasar/WindFM) |
| `windfm-robust` | [NeoQuasar/WindFM-robust](https://huggingface.co/NeoQuasar/WindFM-robust) |

## Moirai 2

`Moirai2Forecaster`. Extra `moirai`, images [`:moirai`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai) / [`:moirai-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=moirai-gpu).

| model | checkpoint |
| --- | --- |
| `moirai-2` | [Salesforce/moirai-2.0-R-small](https://huggingface.co/Salesforce/moirai-2.0-R-small) |

## Moirai 1.x

`MOIRAIForecaster`. Same extra and images as Moirai 2.

| model | checkpoint |
| --- | --- |
| `moirai-1.0-r-small` | [Salesforce/moirai-1.0-R-small](https://huggingface.co/Salesforce/moirai-1.0-R-small) |
| `moirai-1.0-r-base` | [Salesforce/moirai-1.0-R-base](https://huggingface.co/Salesforce/moirai-1.0-R-base) |
| `moirai-1.0-r-large` | [Salesforce/moirai-1.0-R-large](https://huggingface.co/Salesforce/moirai-1.0-R-large) |
| `moirai-1.1-r-small` | [Salesforce/moirai-1.1-R-small](https://huggingface.co/Salesforce/moirai-1.1-R-small) |
| `moirai-1.1-r-base` | [Salesforce/moirai-1.1-R-base](https://huggingface.co/Salesforce/moirai-1.1-R-base) |
| `moirai-1.1-r-large` | [Salesforce/moirai-1.1-R-large](https://huggingface.co/Salesforce/moirai-1.1-R-large) |

## Lag-Llama

`LagLlamaForecaster`. Same extra and images as Moirai.

| model | checkpoint |
| --- | --- |
| `lagllama` | [time-series-foundation-models/Lag-Llama](https://huggingface.co/time-series-foundation-models/Lag-Llama) |

## FlowState

`FlowStateForecaster`. Extra `granite`, images [`:granite`](https://hub.docker.com/r/geetu040/fomo/tags?name=granite) / [`:granite-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=granite-gpu). Revision is pinned to `r1.1`.

| model | checkpoint |
| --- | --- |
| `flowstate` | [ibm-research/flowstate](https://huggingface.co/ibm-research/flowstate) |
| `flowstate-granite` | [ibm-granite/granite-timeseries-flowstate-r1](https://huggingface.co/ibm-granite/granite-timeseries-flowstate-r1) |

## TiRex

`TiRexForecaster`. Extra `tirex`, images [`:tirex`](https://hub.docker.com/r/geetu040/fomo/tags?name=tirex) / [`:tirex-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=tirex-gpu). The registry sets `license_accepted=True`.

| model | checkpoint |
| --- | --- |
| `tirex` | [NX-AI/TiRex](https://huggingface.co/NX-AI/TiRex) |
| `tirex-1.1-gifteval` | [NX-AI/TiRex-1.1-gifteval](https://huggingface.co/NX-AI/TiRex-1.1-gifteval) |

## Toto-2

`Toto2Forecaster`. Extra `toto`, images [`:toto`](https://hub.docker.com/r/geetu040/fomo/tags?name=toto) / [`:toto-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=toto-gpu).

| model | checkpoint |
| --- | --- |
| `toto-2.0-4m` | [Datadog/Toto-2.0-4m](https://huggingface.co/Datadog/Toto-2.0-4m) |
| `toto-2.0-22m` | [Datadog/Toto-2.0-22m](https://huggingface.co/Datadog/Toto-2.0-22m) |
| `toto-2.0-313m` | [Datadog/Toto-2.0-313m](https://huggingface.co/Datadog/Toto-2.0-313m) |
| `toto-2.0-1b` | [Datadog/Toto-2.0-1B](https://huggingface.co/Datadog/Toto-2.0-1B) |
| `toto-2.0-2.5b` | [Datadog/Toto-2.0-2.5B](https://huggingface.co/Datadog/Toto-2.0-2.5B) |

## Mantis

`MantisForecaster`. Extra `mantis`, images [`:mantis`](https://hub.docker.com/r/geetu040/fomo/tags?name=mantis) / [`:mantis-gpu`](https://hub.docker.com/r/geetu040/fomo/tags?name=mantis-gpu). `context_length` is 127; history must be longer than that.

| model | checkpoint |
| --- | --- |
| `mantis` | [paris-noah/MantisV2](https://huggingface.co/paris-noah/MantisV2) |
| `mantis-8m` | [paris-noah/Mantis-8M](https://huggingface.co/paris-noah/Mantis-8M) |
| `mantis-plus` | [paris-noah/MantisPlus](https://huggingface.co/paris-noah/MantisPlus) |

FoMo reads quantile support from the estimator; there is no FoMo capability
flag. The quantile-capable registry families are Naive, TimesFM 2.x, WindFM,
Lag-Llama, FlowState, and Toto-2. Chronos-2, Chronos Bolt, Chronos T5, TTM,
Kronos, Moirai 1.x and 2, TiRex, and Mantis cannot return quantiles.

Load any of these models from [Docker](../server/docker.md) or [from source](../server/source.md), then [predict](../client/http.md).
