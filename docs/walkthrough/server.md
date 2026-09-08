# Server

Load selected models once. Forecasts go to those loaded ids only.

The CLI `fomo serve` constructs [`Server`][fomo.server.serve.Server] and calls `run`. Flags are in the [CLI reference](../reference/cli.md).

## Setting up

### Docker image

Pick a [family tag](docker.md) that contains the extras you need. Extra `docker run` arguments replace the image `CMD` (which otherwise loads `naive`):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

`geetu040/fomo:base` is the same entrypoint with only `naive` available. GPU tags (`hub-gpu`, `full-gpu`, …) need the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) and `--gpus all`.

The image `ENTRYPOINT` already includes `--host 0.0.0.0 --port 8000`. Map the port with `-p 8000:8000`.

Hub checkpoints download on first load. Unauthenticated Hugging Face requests are rate-limited; pass a read token:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN -v "$HOME/.cache/huggingface:/root/.cache/huggingface" geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

### From source

Python >= 3.12. Clone over HTTPS. Use [uv](https://docs.astral.sh/uv/) or pip; FoMo is **not published on PyPI yet**.

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra hub
    uv run fomo serve --host 127.0.0.1 --port 8000 --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,hub]"
    fomo serve --host 127.0.0.1 --port 8000 --load-models naive chronos-bolt-tiny ttm-r3-512-30
    ```

`--extra server` (or `pip install -e ".[server]"`) is enough for `naive`. Add a family extra to match the ids you will load — see [Dependencies](#dependencies). Also install `--extra client` / `.[client]` on machines that call the server with [`Client`][fomo.client.client.Client].

### Server class

Same process, no CLI:

```python
from fomo.server import Server

server = Server(
    load_models=["naive", "chronos-bolt-tiny", "ttm-r3-512-30"],
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
    load_models=["chronos-bolt-tiny", "ttm-r3-512-30", ("naive", NaiveForecaster())],
    host="127.0.0.1",
    port=8000,
).run()
```

`server.app` is the FastAPI app if you want to mount it or pass it to uvicorn yourself.

## Dependencies

Core (always installed) is `pydantic`, `narwhals`, and `pyarrow`. Everything else is an extra. Names match `[project.optional-dependencies]` in `pyproject.toml`.

| extra | pulls in | use |
| --- | --- | --- |
| `http` | `httpx2`, `python-multipart` | HTTP transport |
| `client` | `fomo[http]` | [`Client`][fomo.client.client.Client] talking to a running server |
| `server` | FastAPI, uvicorn, `fomo[sktime]` | `fomo serve` / [`Server`][fomo.server.serve.Server], including `naive` |
| `sktime` | `sktime`, `skpro` | pulled in by `server` |
| `hf` | `fomo[sktime]`, `transformers`, `accelerate` | shared Hub stack |
| `hub` | `fomo[hf]`, `torch` | Chronos Bolt/T5, TTM, TimesFM 2.x |
| `chronos` | `fomo[hf]`, `chronos-forecasting`, `torch` | Chronos-2 |
| `kronos` | `fomo[sktime]`, tokenizer deps, `torch` | Kronos, WindFM |
| `granite` | `fomo[hf]`, `granite-tsfm`, `torch` | FlowState |
| `moirai` | `fomo[hf]`, gluonts/lightning/hydra, `torch` | Moirai, Lag-Llama |
| `tirex` | `fomo[hf]`, `tirex-ts`, `torch` | TiRex |
| `toto` | `fomo[hf]`, `toto-models`, `torch` | Toto-2 |
| `mantis` | `fomo[hf]`, `mantis-tsfm`, `torch` | Mantis |
| `full` | the family extras above | every catalog family |
| `all-extras` | `client` + `server` + `full` | pip stand-in for `uv sync --all-extras` |
| `gpu` | `torch` from PyPI (CUDA / MPS) | pair with a family extra; default lock uses CPU torch |

This site is not an extra. From a clone, `uv sync --group docs` (or `pip install -e ".[docs]"`).

Pick extras to match what the process will do:

| you want | uv | pip (from this clone) |
| --- | --- | --- |
| call a remote server only | `uv sync --extra client` | `pip install -e ".[client]"` |
| serve `naive` | `uv sync --extra server` | `pip install -e ".[server]"` |
| serve TTM / TimesFM / Chronos Bolt | `uv sync --extra server --extra hub` | `pip install -e ".[server,hub]"` |
| serve Chronos-2 | `uv sync --extra server --extra chronos` | `pip install -e ".[server,chronos]"` |
| GPU torch (uv) | add `--extra gpu` | use the `gpu` extra; uv's lock picks the CUDA/MPS index |

A missing executor extra raises `ImportError` at load time (`pip install 'fomo[{name}]'` in the message — that `pip` line is showcase until PyPI exists). A missing *family* extra typically fails later, when `sktime.registry.craft` cannot import the estimator.

Docker bakes extras into the image: `:base` is `server` + `sktime`; `:hub` adds `hub`; `:full` adds `full`. See [Docker](docker.md).

## CLI

```bash
fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30 --host 127.0.0.1 --port 8000 --log-level info
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

Startup logs print the bind URLs. Default bind is [http://127.0.0.1:8000](http://127.0.0.1:8000):

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

`GET /health` is liveness, not “models are warm”. Confirm what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

Then [load more models](models.md) or [send a forecast](http.md).
