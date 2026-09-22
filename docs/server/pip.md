# UV / Pip

Python >= 3.12. Install TServe from PyPI with [uv](https://docs.astral.sh/uv/) or pip, then start `tserve`. Editable installs from a clone stay on [From source](source.md).

## Install

=== "uv"

    ```bash
    uv pip install "tserve[server,hub]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server,hub]"
    ```

    The `gpu` extra does not change a pip install. Family extras already install CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](#gpu).

`server` is enough to serve `naive` (a test baseline). The `hub` extra above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Do not add `client` on a machine that only serves.

## Dependencies

uv and pip both take an extras list on the package. After uv, run `uv run tserve …`. After pip, with the venv on `PATH`, run `tserve …`.

**Naive**

=== "uv"

    ```bash
    uv pip install "tserve[server]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server]"
    ```

**Hub**

=== "uv"

    ```bash
    uv pip install "tserve[server,hub]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server,hub]"
    ```

**Chronos-2**

=== "uv"

    ```bash
    uv pip install "tserve[server,chronos]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server,chronos]"
    ```

**All families** (`full` is the union extra, not `all-extras`. `all-extras` is a pip convenience for `client,server,full` and is not a Docker tag.)

=== "uv"

    ```bash
    uv pip install "tserve[server,full]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server,full]"
    ```

--8<-- "includes/model-dependencies.md"

All 110 supported models are on the [catalog](../models/index.md), and each extra above has a page with its models and a worked `uv` / `pip` install: [base](../models/base.md), [hub](../models/hub.md), [chronos](../models/chronos.md), [kronos](../models/kronos.md), [granite](../models/granite.md), [moirai](../models/moirai.md), [tirex](../models/tirex.md), [toto](../models/toto.md), [mantis](../models/mantis.md), [full](../models/full.md). `gpu` is not a model family; torch CPU vs GPU is in [GPU](#gpu).

## GPU

Family extras pull `torch`. A PyPI install takes the CUDA wheel from PyPI (MPS on macOS).

To **force CPU torch**, install torch from the CPU index first, then TServe. If a later install replaces that wheel with CUDA, run the torch line again.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "tserve[server,hub]"
```

The same order works with `uv pip install`. Swap `hub` for any other family extra from [Dependencies](#dependencies).

The `gpu` extra only selects the torch index in a clone's uv lockfile: [From source](source.md#gpu). Containers use `*-gpu` tags instead: [Docker](docker.md#gpu-images).

## Serve from the command line

=== "uv"

    ```bash
    uv run tserve chronos_bolt ttm_r3
    ```

=== "pip"

    ```bash
    tserve chronos_bolt ttm_r3
    ```

Startup prints the URLs it binds:

```text
Starting TServe
  Dashboard   http://127.0.0.1:8000/
  Swagger UI  http://127.0.0.1:8000/docs
  ReDoc       http://127.0.0.1:8000/redoc
```

`--host` and `--port` move that binding; `127.0.0.1` accepts local connections only, `0.0.0.0` accepts them from your network. `--log-level debug` shows more, `--log-level warning` less. `Ctrl+C` stops the process and exits 0. Catalog models are leftover positionals (`tserve chronos_bolt ttm_r3`). Every flag is in the [CLI reference](../reference/cli.md). Craft specs as `id=spec`: [Craft specs](craft-specs.md).

## Serve from Python

[`Server`][tserve.server.serve.Server] takes the same arguments as the CLI:

```python
from tserve.server import Server

server = Server(
    model=["chronos_bolt", "ttm_r3"],
    host="127.0.0.1",
    port=8000,
)
print(server.url)  # http://127.0.0.1:8000
server.run()
```

Models load during construction, so an unknown model or a missing dependency raises before uvicorn binds the port. `run()` blocks until the process stops. Omitting `model` still loads `naive`, enough to test the process, exactly like a bare `tserve`.

`server.app` is the FastAPI app, for mounting it inside another application or handing it to uvicorn yourself:

```python
import uvicorn

uvicorn.run(server.app, host="127.0.0.1", port=8000, workers=1)
```

Keep it to one worker per process: each worker would load its own copy of every model.

## Next

- [From source](source.md) — editable install from a clone
- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
