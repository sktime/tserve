# Run the server

Start an inference process, then load selected models once. Forecasts go to those loaded ids only.

CLI `fomo serve` constructs [`Server`][fomo.server.serve.Server] and calls [`run`][fomo.server.serve.Server.run]. [`main`][fomo.cli.main.main] is the console-script entry. Flags: [CLI reference](../reference/cli.md).

```bash
fomo serve --load-models naive --host 127.0.0.1 --port 8000
```

| flag | default | |
| --- | --- | --- |
| `--load-models` | none (`[]`) | registry ids to load (`nargs="+"`) |
| `--models-dir` | none | stem rewrite for `.zip` files; does **not** auto-load the directory |
| `--host` | `127.0.0.1` | use `0.0.0.0` in Docker |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | uvicorn log level |

`KeyboardInterrupt` exits 0.

## Empty default vs Docker `CMD`

[`Server(load_models=[])`][fomo.server.serve.Server] and a bare `fomo serve` load nothing. `GET /models` then returns `"models": []`.

The repo `Dockerfile` is different: `CMD` is `--load-models naive`, so `docker run … fomo:local` with no extra args loads `naive`. Pass `--load-models …` on `docker run` to replace that `CMD`. The `ENTRYPOINT` already includes `--host 0.0.0.0 --port 8000`.

## Host and port

`--host` / `--port` are passed to uvicorn. The Python client and curl must use the same origin, for example `Client("http://127.0.0.1:8000")`. [`Server.url`][fomo.server.serve.Server.url] is `http://{host}:{port}` with no path prefix.

After start:

- Dashboard: `http://{host}:{port}/`
- Swagger: `http://{host}:{port}/docs`
- ReDoc: `http://{host}:{port}/redoc`

`--log-level` is the uvicorn log level. [`run`][fomo.server.serve.Server.run] still calls `logging.basicConfig(level=logging.INFO)`.

## Server SDK

```python
from fomo.server import Server

Server(load_models=["naive"], host="127.0.0.1", port=8000).run()
```

See [Embed Server](../use-cases/embed-server.md) and [Load models](load-models.md).
