# TServe

[![Documentation Status](https://readthedocs.org/projects/tserve/badge/?version=latest)](https://tserve.readthedocs.io/en/latest/?badge=latest)

TServe is a local inference server for time-series foundation models. Start the process, load named registry models once, keep them warm, and serve time series forecasts through `POST /predict`, the Python client, or the browser dashboard. TServe also serves its own OpenAPI documentation. It does not provide a hosted API.

- [Documentation](https://tserve.readthedocs.io)
- [Docker Hub](https://hub.docker.com/r/sktime/tserve)
- Clone: `https://github.com/sktime/tserve.git`

## Quick start

### Docker

The `hub` image includes the dependencies for Chronos Bolt/T5, TTM, and TimesFM 2.x. This command loads two registry models:

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
```

Tags cover other families too. For example, the `moirai` image can load `moirai_2`:

```bash
docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
```

Choose a model and its matching image tag from the [model catalog](https://tserve.readthedocs.io/en/latest/models/). The process always loads `naive` for testing; name extra models alongside it for a real forecast.

### UV / Pip

TServe requires Python 3.12 or newer. Install `server` plus the family extra for the models you need, and start the process. These commands work line by line in macOS/Linux shells and Windows PowerShell.

**uv**

```bash
uv pip install "tserve[server,hub]"
```

```bash
uv run tserve chronos_bolt ttm_r3
```

**pip**

The `gpu` extra does not work with pip. Family extras already install CUDA torch from PyPI (MPS on macOS). Do not add `gpu` to the extras list.

```bash
python -m pip install "tserve[server,hub]"
```

```bash
tserve chronos_bolt ttm_r3
```

To force a CPU wheel, install torch from the CPU index first, then TServe. If pip later replaces it with CUDA, run the torch line again.

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install "tserve[server,hub]"
```

The `server` extra alone is enough for `naive` (a test baseline). Do not install `client` on a server-only machine. See [UV / Pip](https://tserve.readthedocs.io/en/latest/server/pip/) for family extras, GPU installs, and Python-based server setup.

### From source

Clone over HTTPS for an editable install. These commands work line by line in macOS/Linux shells and Windows PowerShell.

**uv**

```bash
git clone https://github.com/sktime/tserve.git
cd tserve
uv sync --extra server --extra hub
```

```bash
uv run tserve chronos_bolt ttm_r3
```

**pip**

The `gpu` extra does not work with pip. Family extras already install CUDA torch from PyPI (MPS on macOS). Do not add `gpu` to the extras list.

```bash
git clone https://github.com/sktime/tserve.git
cd tserve
python -m pip install -e ".[server,hub]"
```

```bash
tserve chronos_bolt ttm_r3
```

To force a CPU wheel, install torch from the CPU index first, then TServe. If pip later replaces it with CUDA, run the torch line again.

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[server,hub]"
```

See [From source](https://tserve.readthedocs.io/en/latest/server/source/) for the clone walkthrough.

## Predict

A predict request describes a table and the roles of its columns:

- `past` is the historical table: one row per timestamp, with time, target, and optional feature columns. Time must be a column, not a pandas index.
- `time` names the time column, and `target` names the column or columns to forecast.
- `fh` is the number of steps ahead and must be greater than zero.
- `model` is a model already loaded by this server.
- `future`, `static`, and `quantiles` are optional.

`quantiles` requires an estimator that supports quantile prediction, such as `timesfm_2_5`; `ttm_r3` does not.

`past` is not a one-dimensional vector. See the [data specification](https://tserve.readthedocs.io/en/latest/client/data/) for supported table shapes, inference rules, static data, quantiles, and current limitations.

### curl

This sends five days of sales and asks `chronos_bolt` for the next three. The JSON after `-d` stays on one line for copy-paste reliability.

**macOS / Linux**

```bash
curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
```

**Windows PowerShell**

Use `curl.exe` so PowerShell does not substitute `Invoke-WebRequest`.

```powershell
curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
```

`POST /predict` returns column-oriented JSON containing `predictions`, `quantiles`, `model`, and `request_id`.

### Python

Install the client extra:

**uv**

```bash
uv pip install "tserve[client]"
```

**pip**

```bash
python -m pip install "tserve[client]"
```

Then send the same fields:

```python
from tserve.client import Client

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
    result = client.predict(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="chronos_bolt",
    )

print(result.predictions)
```

The client accepts dictionaries, pandas, polars, pyarrow, and Narwhals tables, posts Arrow to `/predict/bytes`, and restores results to the input table type. See the [Python guide](https://tserve.readthedocs.io/en/latest/client/python/).

## Choose and load models

TServe has named models for Chronos, Chronos Bolt, TTM, TimesFM, Moirai, Toto, TiRex, FlowState, Kronos, Mantis, Lag-Llama, and the `naive` baseline. To load one:

1. Find its exact name in the [catalog](https://tserve.readthedocs.io/en/latest/models/).
2. Install the listed family extra, or pull the matching Docker tag.
3. Name the model on `tserve` as leftover positionals.

The catalog is what a TServe process *can* load. `GET /models` reports only what the current process *did* load.

## Docker images

Images are published as:

- `base` for `naive`;
- `hub` for the shared Chronos Bolt/T5, TTM, and TimesFM stack;
- family tags such as `chronos`, `granite`, `kronos`, `moirai`, `tirex`, `toto`, and `mantis` (`kronos` sits on `base`, not `hub`);
- `full` for every family;
- matching `*-gpu` variants for every family tag and `full`.

GPU containers require an NVIDIA GPU, the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), and `--gpus all`:

```bash
docker run --rm --gpus all -p 8000:8000 sktime/tserve:hub-gpu chronos_bolt ttm_r3
```

For Hugging Face rate limits, set a read token in your environment and forward it. In bash/zsh use `export HF_TOKEN=hf_your_token`; in PowerShell use `$env:HF_TOKEN = "hf_your_token"`. Then run:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN sktime/tserve:hub chronos_bolt
```

Keep downloaded weights across containers with a portable named volume:

```bash
docker run --rm -p 8000:8000 -v tserve-hf:/root/.cache/huggingface sktime/tserve:hub chronos_bolt ttm_r3
```

The [Docker guide](https://tserve.readthedocs.io/en/latest/server/docker/) covers all tags, host cache mounts, GPU constraints, saved models, and local builds.

## Server behavior and options

A bare `tserve` still loads `naive`, enough to test the process. Name extra registry models as leftover positionals (`tserve chronos_bolt ttm_r3`) for a real forecast. `--models-dir` selects sktime `.zip` files, `--host` and `--port` change the binding, and `--log-level` changes verbosity.

`GET /health` checks process liveness. `GET /models` lists loaded models. `GET /stats` reports process and per-model metrics. See the [CLI reference](https://tserve.readthedocs.io/en/latest/reference/cli/), or serve [saved models](https://tserve.readthedocs.io/en/latest/server/models-dir/), [live estimator objects](https://tserve.readthedocs.io/en/latest/server/live-objects/), or [craft specs](https://tserve.readthedocs.io/en/latest/server/craft-specs/).

## HTTP and Python clients

Use JSON `POST /predict` from any language. The Python `Client` sends the same fields as Arrow to `POST /predict/bytes`. Prediction is POST-only: `GET /predict` returns 405 Method Not Allowed.

Every URL in this README belongs to the TServe process you started; there is no hosted TServe endpoint. See the [HTTP guide](https://tserve.readthedocs.io/en/latest/client/http/) and [Python guide](https://tserve.readthedocs.io/en/latest/client/python/) for complete examples.

## Dashboard and OpenAPI

After the server starts, open:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

The [dashboard](https://tserve.readthedocs.io/en/latest/server/dashboard/) can load sample or CSV data, select a loaded model, plot forecasts, show health and stats, and download results.

## Documentation

- [Server](https://tserve.readthedocs.io/en/latest/server/)
- [Docker](https://tserve.readthedocs.io/en/latest/server/docker/)
- [UV / Pip](https://tserve.readthedocs.io/en/latest/server/pip/)
- [From source](https://tserve.readthedocs.io/en/latest/server/source/)
- [Model catalog and dependencies](https://tserve.readthedocs.io/en/latest/models/)
- [HTTP client](https://tserve.readthedocs.io/en/latest/client/http/)
- [Python client](https://tserve.readthedocs.io/en/latest/client/python/)
- [Data specification](https://tserve.readthedocs.io/en/latest/client/data/)
- [HTTP API reference](https://tserve.readthedocs.io/en/latest/reference/http/)
- [CLI reference](https://tserve.readthedocs.io/en/latest/reference/cli/)
- [Python API reference](https://tserve.readthedocs.io/en/latest/reference/api/)
- [Errors](https://tserve.readthedocs.io/en/latest/reference/errors/)
- [Development](https://tserve.readthedocs.io/en/latest/reference/development/)

## Contributing and license

See the [development guide](https://tserve.readthedocs.io/en/latest/reference/development/) for setup, checks, tests, documentation, and image builds. Issues are tracked on [GitHub](https://github.com/sktime/tserve/issues).

TServe is licensed under the BSD 3-Clause License. See [LICENSE](LICENSE).
