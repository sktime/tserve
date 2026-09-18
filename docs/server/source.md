# From source

Python >= 3.12, and a clone over HTTPS. FoMo is **not on PyPI yet**, so installs come from the repo. [uv](https://docs.astral.sh/uv/) is the shorter path, pip works everywhere.

## Install

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra hub
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,hub]"
    ```

    The `gpu` extra does not work with pip. Family extras already install CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](#gpu).

`server` is enough to serve `naive`. The `hub` extra above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Do not add `client` on a machine that only serves.

## Dependencies

uv repeats `--extra`. pip takes one extras list. After uv, run `uv run fomo serve …`. After pip, with the venv on `PATH`, run `fomo serve …`.

**Naive**

=== "uv"

    ```bash
    uv sync --extra server
    ```

=== "pip"

    ```bash
    pip install -e ".[server]"
    ```

**Hub**

=== "uv"

    ```bash
    uv sync --extra server --extra hub
    ```

=== "pip"

    ```bash
    pip install -e ".[server,hub]"
    ```

**Chronos-2**

=== "uv"

    ```bash
    uv sync --extra server --extra chronos
    ```

=== "pip"

    ```bash
    pip install -e ".[server,chronos]"
    ```

**All families** (`full` is the union extra, not `all-extras`. `all-extras` is a pip convenience for `client,server,full` and is not a Docker tag.)

=== "uv"

    ```bash
    uv sync --extra server --extra full
    ```

=== "pip"

    ```bash
    pip install -e ".[server,full]"
    ```

--8<-- "includes/model-dependencies.md"

All 110 supported models are on the [catalog](../models/index.md), and each extra above has a page with its ids and a worked `uv` / `pip` install: [base](../models/base.md), [hub](../models/hub.md), [chronos](../models/chronos.md), [kronos](../models/kronos.md), [granite](../models/granite.md), [moirai](../models/moirai.md), [tirex](../models/tirex.md), [toto](../models/toto.md), [mantis](../models/mantis.md), [full](../models/full.md). `gpu` is not a model family; torch CPU vs GPU is in [GPU](#gpu).

## GPU

Family extras pull `torch`. Which wheel you get depends on the installer.

**uv** defaults to the CPU index. Add `--extra gpu` for the PyPI wheel: CUDA on Linux and Windows, MPS on Apple silicon. Pair it with the family extras you need.

```bash
uv sync --extra server --extra hub --extra gpu
```

**pip** does not honor the `gpu` extra. `pip install -e ".[server,hub,gpu]"` is the same as without `gpu`. A normal pip install always takes CUDA torch from PyPI (MPS on macOS).

To **force CPU torch with pip**, install torch from the CPU index first, then FoMo. If a later `pip install` replaces that wheel with CUDA, run the torch line again.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[server,hub]"
```

Swap `hub` for any other family extra from [Dependencies](#dependencies). Containers use `*-gpu` tags instead: [Docker](docker.md#gpu-images).

## Serve from the command line

=== "uv"

    ```bash
    uv run fomo serve --model chronos-bolt ttm-r3
    ```

=== "pip"

    ```bash
    fomo serve --model chronos-bolt ttm-r3
    ```

Startup prints the URLs it binds:

```text
Starting FoMo
  Dashboard   http://127.0.0.1:8000/
  Swagger UI  http://127.0.0.1:8000/docs
  ReDoc       http://127.0.0.1:8000/redoc
```

`--host` and `--port` move that binding; `127.0.0.1` accepts local connections only, `0.0.0.0` accepts them from your network. `--log-level debug` shows more, `--log-level warning` less. `Ctrl+C` stops the process and exits 0. Catalog ids can also be leftover positionals (`fomo serve chronos-bolt ttm-r3`); `--model` still works and combines with them. Every flag is in the [CLI reference](../reference/cli.md). Craft specs as `id=spec`: [Craft specs](craft-specs.md).

## Serve from Python

[`Server`][fomo.server.serve.Server] takes the same arguments as the CLI:

```python
from fomo.server import Server

server = Server(
    model=["chronos-bolt", "ttm-r3"],
    host="127.0.0.1",
    port=8000,
)
print(server.url)  # http://127.0.0.1:8000
server.run()
```

Models load during construction, so an unknown id or a missing dependency raises before uvicorn binds the port. `run()` blocks until the process stops. Omitting `model` still loads `naive`, exactly like a bare `fomo serve`.

`server.app` is the FastAPI app, for mounting it inside another application or handing it to uvicorn yourself:

```python
import uvicorn

uvicorn.run(server.app, host="127.0.0.1", port=8000, workers=1)
```

Keep it to one worker per process: each worker would load its own copy of every model.

## Next

- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
