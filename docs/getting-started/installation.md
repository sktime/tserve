# Installation

Python >= 3.12. Packaging uses [uv](https://docs.astral.sh/uv/) and hatchling.

Core dependencies (always installed) are `pydantic`, `narwhals`, and `pyarrow`. Optional extras add the HTTP client, the FastAPI server, or sktime estimators.

## Extras

Install only what the process will use. Names match `[project.optional-dependencies]` in `pyproject.toml`.

| extra | pulls in | use |
| --- | --- | --- |
| `http` | `httpx`, `python-multipart` | [`HttpTransport`][fomo.client.transports.http.HttpTransport] |
| `client` | `fomo[http]` | [`Client`][fomo.client.client.Client] talking to a running server |
| `server` | `fastapi`, `python-multipart`, `uvicorn` | `fomo serve` / [`Server`][fomo.server.serve.Server] |
| `sktime-lite` | `sktime` | [`SktimeExecutor`][fomo.runtime.executors.sktime.executor.SktimeExecutor] and registry id `naive` (`NaiveForecaster`) |
| `sktime` | `sktime` plus Hub-model deps (`torch`, `transformers`, estimator packages, …) | registry ids other than `naive` |
| `pytorch-forecasting` | `pytorch-forecasting` | extra exists; [`PytorchForecastingExecutor`][fomo.runtime.executors.pytorch_forecasting.executor.PytorchForecastingExecutor] raises `NotImplementedError` |
| `docs` | Material, mkdocstrings, plus `server` / `http` / `sktime-lite` | this documentation site |

`client` is enough on a machine that only calls a running server. A process that loads models needs `server` plus an executor extra (`sktime-lite` for `naive`, `sktime` for Hub estimators). See [Extras and Hub weights](../how-to/extras.md).

A missing executor extra raises `ImportError` at load time: install with `pip install 'fomo[{name}]'` where `{name}` is the executor plugin (`sktime` or `pytorch-forecasting`).

## From source

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
uv sync
uv run fomo serve --load-models naive
```

`uv sync` without extras does not install `server` or `sktime`. For a local server that can load `naive` and a client in the same environment:

```bash
uv pip install -e '.[server,sktime-lite,client]'
fomo serve --load-models naive
```

Hub ids such as `chronos-2` need the `sktime` extra (or equivalent packages already in the environment):

```bash
uv pip install -e '.[server,sktime]'
fomo serve --load-models naive chronos-2
```

## Docker: pre-built image

```bash
docker run --rm -p 8000:8000 \
  docker.io/sktime/fomo:dl-py3.13 \
  fomo serve --host 0.0.0.0 --port 8000 --load-models naive
```

## Docker: from this repo

The repo [`Dockerfile`](https://github.com/sktime/fomo/blob/main/Dockerfile) always installs `server` and `sktime-lite`. The image `ENTRYPOINT` is `fomo serve --host 0.0.0.0 --port 8000`. The image `CMD` is `--load-models naive`, so `docker run` with no extra args loads `naive`. Extra `docker run` arguments replace that `CMD`.

Add heavier extras at build time:

```bash
git clone git@github.com:sktime/fomo.git
cd fomo
docker build -t fomo:local .
docker run --rm -p 8000:8000 fomo:local
# Hub models:
# docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
# docker run --rm -p 8000:8000 fomo:sktime --load-models naive chronos-2
```

Bare `fomo serve` / [`Server()`][fomo.server.serve.Server] with no `load_models` still starts empty. The Docker `CMD` is an image default, not the Python default.

## Custom image

Add extra Python deps on top of the published image:

```dockerfile
FROM docker.io/sktime/fomo:dl-py3.13

RUN pip install my-package another-package
```

```bash
docker build -t my-fomo:custom .
docker run --rm -p 8000:8000 \
  my-fomo:custom \
  fomo serve --host 0.0.0.0 --port 8000 --load-models naive
```
