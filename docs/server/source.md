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

`server` is enough to serve `naive`. Each model family is its own extra — `hub` above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Pick the ones matching the ids you plan to load; extras and tags are on [Load models](../models/index.md#which-extra-image).

## Serve from the command line

```bash
uv run fomo serve --load-models chronos-bolt-tiny timesfm-2.5
```

Without uv, drop the prefix and call `fomo serve` directly. Startup prints the URLs it binds:

```text
Starting FoMo
  Dashboard   http://127.0.0.1:8000/
  Swagger UI  http://127.0.0.1:8000/docs
  ReDoc       http://127.0.0.1:8000/redoc
```

`--host` and `--port` move that binding; `127.0.0.1` accepts local connections only, `0.0.0.0` accepts them from your network. `--log-level debug` shows more, `--log-level warning` less. `Ctrl+C` stops the process and exits 0. Every flag is in the [CLI reference](../reference/cli.md).

## Serve from Python

[`Server`][fomo.server.serve.Server] takes the same arguments as the CLI:

```python
from fomo.server import Server

server = Server(
    load_models=["chronos-bolt-tiny", "timesfm-2.5"],
    host="127.0.0.1",
    port=8000,
)
print(server.url)  # http://127.0.0.1:8000
server.run()
```

Models load during construction, so an unknown id or a missing dependency raises before uvicorn binds the port. `run()` blocks until the process stops. Omitting `load_models` starts empty, exactly like a bare `fomo serve`.

`server.app` is the FastAPI app, for mounting it inside another application or handing it to uvicorn yourself:

```python
import uvicorn

uvicorn.run(server.app, host="127.0.0.1", port=8000, workers=1)
```

Keep it to one worker per process: each worker would load its own copy of every model.

## Next

- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
