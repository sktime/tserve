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

```bash
tserve --host 0.0.0.0 --port 9000 --log-level warning chronos_bolt ttm_r3
```

`--host 127.0.0.1` accepts local connections only. `0.0.0.0` also accepts them from your network. `--log-level` is `debug`, `info`, `warning`, `error`, or `critical`. `Ctrl+C` stops the process and exits 0. Every flag: [CLI](../reference/cli.md). A craft spec is `id=spec`: [Craft specs](craft-specs.md).

## Serve from Python

[`Server`][tserve.server.serve.Server] takes the same arguments:

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

Models load during construction, so an unknown model or a missing dependency raises before the port is bound. `run()` blocks until the process stops. Omitting `model` still loads `naive`.

`server.app` is the FastAPI app:

```python
import uvicorn

uvicorn.run(server.app, host="127.0.0.1", port=8000, workers=1)
```

Use one worker per process. Each worker loads its own copy of every model.
