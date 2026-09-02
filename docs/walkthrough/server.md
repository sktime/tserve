# Server

Load selected models once. Forecasts go to those loaded ids only.

The CLI `fomo serve` constructs [`Server`][fomo.server.serve.Server] and calls `run`. Flags are in the [CLI reference](../reference/cli.md).

## Setting up

### Docker image

The sktime image can load registry models. Extra `docker run` arguments replace the image `CMD` (which otherwise loads `naive`):

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

`geetu040/fomo:base` is the same entrypoint with only `naive` available — useful for tests and CI. See the [Docker walkthrough](docker.md) for GPU, volume mounts, building locally, and custom images.

The image `ENTRYPOINT` already includes `--host 0.0.0.0 --port 8000`. Map the port with `-p 8000:8000`.

### From source

Python >= 3.12. Uses [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:sktime/fomo.git && cd fomo
uv sync --all-extras
uv run fomo serve --host 127.0.0.1 --port 8000 \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

`--all-extras` is the blunt option (server, client, Hub-model deps). To install less, see [Dependencies](#dependencies).

### Install from PyPI

FoMo is **not published on PyPI yet**. The commands below are a showcase of what the install will look like:

```bash
pip install 'fomo[server,sktime,client]'   # not on PyPI yet
fomo serve --host 127.0.0.1 --port 8000 \
  --load-models naive flowstate tirex
```

Until then, install from a clone (`uv sync --all-extras` or `uv pip install -e '.[server,sktime,client]'`).

### Server class

Same process, no CLI:

```python
from fomo.server import Server

server = Server(
    load_models=["naive", "kronos", "moirai-2", "flowstate"],
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
    load_models=["timesfm-2.5", "ttm-r3-52-16", ("naive", NaiveForecaster())],
    host="127.0.0.1",
    port=8000,
).run()
```

`server.app` is the FastAPI app if you want to mount it or pass it to uvicorn yourself.

## Dependencies

Core (always installed) is `pydantic`, `narwhals`, and `pyarrow`. Everything else is an extra. Names match `[project.optional-dependencies]` in `pyproject.toml`.

| extra | pulls in | use |
| --- | --- | --- |
| `http` | `httpx`, `python-multipart` | HTTP transport |
| `client` | `fomo[http]` | [`Client`][fomo.client.client.Client] talking to a running server |
| `server` | `fastapi`, `python-multipart`, `uvicorn` | `fomo serve` / [`Server`][fomo.server.serve.Server] |
| `sktime-lite` | `sktime` | registry id `naive` |
| `sktime` | `sktime` plus Hub deps (`torch`, `transformers`, estimator packages, …) | other registry ids |
| `pytorch-forecasting` | `pytorch-forecasting` | extra exists; the executor is not implemented yet |
| `docs` | Material, mkdocstrings, plus `server` / `http` / `sktime-lite` | this documentation site |

Pick extras to match what the process will do:

| you want | install |
| --- | --- |
| call a remote server only | `uv sync --extra client` |
| serve `naive` | `uv sync --extra server --extra sktime-lite` |
| serve Hub models | `uv sync --extra server --extra sktime` |
| local server + client + Hub models | `uv sync --all-extras` |

A missing executor extra raises `ImportError` at load time (`pip install 'fomo[{name}]'` in the message — that `pip` line is also showcase until PyPI exists).

Docker bakes extras into the image: `:base` is `server` + `sktime-lite`; `:sktime` adds the `sktime` extra. See [Docker](docker.md).

## CLI

```bash
fomo serve \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m \
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
```

Then [load more models](models.md) or [send a forecast](client.md).
