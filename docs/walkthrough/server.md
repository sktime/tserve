# Server

Load selected models once. Forecasts go to those loaded ids only.

The CLI `fomo serve` constructs [`Server`][fomo.server.serve.Server] and calls `run`. Flags are in the [CLI reference](../reference/cli.md).

## Setting up

### Docker image

The sktime image can load registry models. Extra `docker run` arguments replace the image `CMD` (which otherwise loads `naive`):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2
```

`geetu040/fomo:base` is the same entrypoint with only `naive` available — useful for tests and CI. See the [Docker walkthrough](docker.md) for GPU, building locally, and custom images.

The image `ENTRYPOINT` already includes `--host 0.0.0.0 --port 8000`. Map the port with `-p 8000:8000`.

### From source

Python >= 3.12. Uses [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:sktime/fomo.git && cd fomo
uv sync --extra server --extra sktime-lite --extra client
uv run fomo serve --host 127.0.0.1 --port 8000 --load-models naive
```

Hub ids such as `chronos-2` need the `sktime` extra (torch, transformers, estimator packages):

```bash
uv sync --extra server --extra sktime --extra client
uv run fomo serve --host 127.0.0.1 --port 8000 --load-models naive chronos-2
```

Install only what the process will use:

| extra | use |
| --- | --- |
| `client` | [`Client`][fomo.client.client.Client] talking to a running server |
| `server` | `fomo serve` / [`Server`][fomo.server.serve.Server] |
| `sktime-lite` | registry id `naive` |
| `sktime` | other registry ids (Hub checkpoints) |

`client` is enough on a machine that only calls a remote server. A process that loads models needs `server` plus `sktime-lite` or `sktime`.

### Install from PyPI

Not published yet. When it is:

```bash
pip install 'fomo[server,sktime-lite,client]'
fomo serve --host 127.0.0.1 --port 8000 --load-models naive
```

### Server class

Same process, no CLI:

```python
from fomo.server import Server

server = Server(
    load_models=["naive", "chronos-2"],
    host="127.0.0.1",
    port=8000,
)
print(server.url)  # http://127.0.0.1:8000
server.run()
```

Omitting `load_models` starts empty, same as a bare `fomo serve`. You can mix registry ids and live objects:

```python
from fomo.server import Server
from sktime.forecasting.naive import NaiveForecaster

Server(
    load_models=["chronos-2", ("naive", NaiveForecaster())],
    host="127.0.0.1",
    port=8000,
).run()
```

`server.app` is the FastAPI app if you want to mount it or pass it to uvicorn yourself.

## CLI

```bash
fomo serve \
  --load-models naive chronos-2 \
  --host 127.0.0.1 \
  --port 8000 \
  --log-level info
```

| flag | default | |
| --- | --- | --- |
| `--load-models` | none | registry ids to load |
| `--models-dir` | none | rewrite matching `.zip` stems already named in `--load-models` |
| `--host` | `127.0.0.1` | use `0.0.0.0` in Docker |
| `--port` | `8000` | |
| `--log-level` | `info` | uvicorn log level |

`--load-models` takes names only. `(id, estimator)` pairs are SDK-only. Unknown registry ids fail during construction, before uvicorn starts. `KeyboardInterrupt` exits 0.

## After start

Default bind is [http://127.0.0.1:8000](http://127.0.0.1:8000):

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

`GET /health` is liveness, not “models are warm”. Confirm what loaded:

```bash
curl -s http://127.0.0.1:8000/models
# {"models":[{"id":"naive","executor":"sktime","source":"registry"}]}
```

Then [load more models](models.md) or [send a forecast](client.md).
