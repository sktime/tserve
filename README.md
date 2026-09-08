# FoMo

[![Documentation Status](https://readthedocs.org/projects/fomo/badge/?version=latest)](https://fomo.readthedocs.io/en/latest/?badge=latest)

FoMo is a local inference server for time-series foundation models. Start the
process, load named registry ids once, keep them warm, and forecast through
`POST /forecast`, the Python client, or the browser dashboard. The process also
serves its own OpenAPI documentation. FoMo does not provide a hosted API.

- [Documentation](https://fomo.readthedocs.io)
- [Docker Hub](https://hub.docker.com/r/geetu040/fomo)
- Clone: `https://github.com/sktime/fomo.git`

## Quick start

### Docker

The `hub` image includes the dependencies for Chronos Bolt/T5, TTM, and
TimesFM 2.x. This command loads two registry ids:

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt-tiny timesfm-2.5
```

Tags cover other families too. For example, the `moirai` image can load
`moirai-2`:

```bash
docker run --rm -p 8000:8000 geetu040/fomo:moirai --load-models moirai-2
```

Choose an id and its matching image tag from the
[model catalog](https://fomo.readthedocs.io/en/latest/models/). With no
arguments, an image loads `naive` through its image `CMD`.

### From source

FoMo requires Python 3.12 or newer and is not on PyPI yet. Clone it over HTTPS,
install `server` plus the family extra for the ids you need, and start the
process. These commands work line by line in macOS/Linux shells and Windows
PowerShell.

**uv**

```bash
git clone https://github.com/sktime/fomo.git
cd fomo
uv sync --extra server --extra hub
uv run fomo serve --load-models chronos-bolt-tiny timesfm-2.5
```

**pip**

```bash
git clone https://github.com/sktime/fomo.git
cd fomo
python -m pip install -e ".[server,hub]"
fomo serve --load-models chronos-bolt-tiny timesfm-2.5
```

The `server` extra alone is enough for `naive`. Do not install `client` on a
server-only machine. See [Server](https://fomo.readthedocs.io/en/latest/server/)
for family extras, GPU installs, and Python-based server setup.

## Forecast

A forecast request describes a table and the roles of its columns:

- `past` is the historical table: one row per timestamp, with time, target,
  and optional feature columns. Time must be a column, not a pandas index.
- `time` names the time column, and `target` names the column or columns to
  forecast.
- `fh` is the number of steps ahead and must be greater than zero.
- `model` is an id already loaded by this server.
- `future`, `static`, and `quantiles` are optional.

`past` is not a one-dimensional vector. See the
[data specification](https://fomo.readthedocs.io/en/latest/client/data/) for
supported table shapes, inference rules, static data, quantiles, and current
limitations.

### curl

This sends five days of sales and asks `chronos-bolt-tiny` for the next three.
The JSON after `-d` stays on one line for copy-paste reliability.

**macOS / Linux**

```bash
curl -s http://127.0.0.1:8000/forecast -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos-bolt-tiny"}'
```

**Windows PowerShell**

Use `curl.exe` so PowerShell does not substitute `Invoke-WebRequest`.

```powershell
curl.exe -s http://127.0.0.1:8000/forecast -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos-bolt-tiny"}'
```

`POST /forecast` returns column-oriented JSON containing `predictions`,
`quantiles`, `model`, and `request_id`.

### Python

Install the client extra in a clone:

**uv**

```bash
uv sync --extra client
```

**pip**

```bash
python -m pip install -e ".[client]"
```

Then send the same fields:

```python
from fomo.client import Client

past = {
    "timestamp": [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
    ],
    "sales": [120, 135, 128, 142, 138],
}

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="chronos-bolt-tiny",
    )

print(result.predictions)
```

The client accepts dictionaries, pandas, polars, pyarrow, and Narwhals tables,
posts Arrow to `/forecast/bytes`, and restores results to the input table type.
See the [Python guide](https://fomo.readthedocs.io/en/latest/client/python/).

## Choose and load models

FoMo has named ids for Chronos, Chronos Bolt, TTM, TimesFM, Moirai, Toto,
TiRex, FlowState, Kronos, Mantis, Lag-Llama, and the `naive` baseline. To load
one:

1. Find its exact id in the [catalog](https://fomo.readthedocs.io/en/latest/models/).
2. Install the listed family extra, or pull the matching Docker tag.
3. Name the id in `--load-models`.

The catalog is what a process *can* load. `GET /models` reports only what the
current process *did* load.

## Docker images

Images are published as:

- `base` for `naive`;
- `hub` for the shared Chronos Bolt/T5, TTM, and TimesFM stack;
- family tags such as `chronos`, `granite`, `kronos`, `moirai`, `tirex`,
  `toto`, and `mantis`;
- `full` for every family;
- matching `*-gpu` variants for every family tag and `full`.

GPU containers require an NVIDIA GPU, the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html),
and `--gpus all`:

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:hub-gpu --load-models chronos-bolt-tiny timesfm-2.5
```

For Hugging Face rate limits, set a read token in your environment and forward
it. In bash/zsh use `export HF_TOKEN=hf_your_token`; in PowerShell use
`$env:HF_TOKEN = "hf_your_token"`. Then run:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN geetu040/fomo:hub --load-models chronos-bolt-tiny
```

Keep downloaded weights across containers with a portable named volume:

```bash
docker run --rm -p 8000:8000 -v fomo-hf:/root/.cache/huggingface geetu040/fomo:hub --load-models chronos-bolt-tiny timesfm-2.5
```

The [Docker guide](https://fomo.readthedocs.io/en/latest/server/docker/) covers
all tags, host cache mounts, GPU constraints, saved models, and local builds.

## Server behavior and options

A bare `fomo serve` loads nothing. Use `--load-models` to select registry ids,
`--models-dir` for selected sktime `.zip` files, `--host` and `--port` to
change the binding, and `--log-level` to change verbosity. The image default
that loads `naive` is not the Python or CLI default.

`GET /health` checks process liveness. `GET /models` lists loaded ids.
`GET /stats` reports process and per-model metrics. See the
[CLI reference](https://fomo.readthedocs.io/en/latest/reference/cli/), or
serve [saved models](https://fomo.readthedocs.io/en/latest/server/models-dir/)
and [live estimator objects](https://fomo.readthedocs.io/en/latest/server/live-objects/).

## HTTP and Python clients

Use JSON `POST /forecast` from any language. The Python `Client` sends the same
fields as Arrow to `POST /forecast/bytes`. Forecasting is POST-only:
`GET /forecast` returns 405 Method Not Allowed.

Every URL in this README belongs to the FoMo process you started; there is no
hosted FoMo endpoint. See the [HTTP guide](https://fomo.readthedocs.io/en/latest/client/http/)
and [Python guide](https://fomo.readthedocs.io/en/latest/client/python/) for
complete examples.

## Dashboard and OpenAPI

After the server starts, open:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

The [dashboard](https://fomo.readthedocs.io/en/latest/server/dashboard/) can
load sample or CSV data, select a loaded model, plot forecasts, show health
and stats, and download results.

## Documentation

- [Server](https://fomo.readthedocs.io/en/latest/server/)
- [Docker](https://fomo.readthedocs.io/en/latest/server/docker/)
- [From source](https://fomo.readthedocs.io/en/latest/server/source/)
- [Model catalog and dependencies](https://fomo.readthedocs.io/en/latest/models/)
- [HTTP client](https://fomo.readthedocs.io/en/latest/client/http/)
- [Python client](https://fomo.readthedocs.io/en/latest/client/python/)
- [HTTP API reference](https://fomo.readthedocs.io/en/latest/reference/http/)
- [CLI reference](https://fomo.readthedocs.io/en/latest/reference/cli/)
- [Python API reference](https://fomo.readthedocs.io/en/latest/reference/api/)
- [Errors](https://fomo.readthedocs.io/en/latest/reference/errors/)
- [Development](https://fomo.readthedocs.io/en/latest/reference/development/)

## Contributing and license

See the [development guide](https://fomo.readthedocs.io/en/latest/reference/development/)
for setup, checks, tests, documentation, and image builds. Issues are tracked
on [GitHub](https://github.com/sktime/fomo/issues).

FoMo is licensed under the [MIT License](LICENSE).
