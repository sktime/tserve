# TServe

[![Documentation Status](https://readthedocs.org/projects/tserve/badge/?version=latest)](https://tserve.readthedocs.io/en/latest/?badge=latest)

Time series serving for foundation models. Load models once, keep them warm, and forecast from HTTP or from Python. TServe is a server you run, not a hosted API.

- [Documentation](https://tserve.readthedocs.io)
- [Docker Hub](https://hub.docker.com/r/sktime/tserve)

## Install

Python 3.12 or newer for a local install. Docker needs no local Python. The `hub` image loads Chronos Bolt/T5, TTM, and TimesFM.

**Docker**

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
```

```bash
docker run --rm --gpus all -p 8000:8000 sktime/tserve:hub-gpu chronos_bolt ttm_r3
```

Forward a Hugging Face token and keep the weights:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN -v tserve-hf:/root/.cache/huggingface sktime/tserve:hub chronos_bolt ttm_r3
```

**uv**

```bash
uv pip install "tserve[server,hub]"
uv run tserve chronos_bolt ttm_r3
```

**pip**

```bash
python -m pip install "tserve[server,hub]"
tserve chronos_bolt ttm_r3
```

A PyPI install takes CUDA torch (MPS on macOS). For a CPU wheel, install torch from the CPU index first:

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install "tserve[server,hub]"
```

`server` alone is enough for `naive`. Do not install `client` on a machine that only serves. Other families, a clone, and the `gpu` extra: [Installation](https://tserve.readthedocs.io/en/latest/installation/), [From source](https://tserve.readthedocs.io/en/latest/server/source/).

## Forecast

**curl**

```bash
curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
  "past": {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    "sales": [120, 135, 128, 142, 138]
  },
  "fh": 3,
  "model": "chronos_bolt"
}'
```

**PowerShell**

```powershell
curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"fh":3,"model":"chronos_bolt"}'
```

The response is column-oriented JSON: `predictions`, `quantiles`, `model`, `request_id`.

**Python**

```bash
uv pip install "tserve[client]"
```

```python
from tserve.client import Client

past = {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
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

`past` can be a dict, pandas, polars, pyarrow, or Narwhals table. The result comes back as that same type. Time has to be a column (`reset_index()` first). Every field: [data specification](https://tserve.readthedocs.io/en/latest/client/data/).

## Models

`naive` always loads and downloads nothing. `GET /models` lists what this process loaded. One image cannot mix `kronos` with a hub model; `:full` can.

Images are `sktime/tserve:<tag>`.

| extra | tag | loads | example |
| --- | --- | --- | --- |
| `server` | `base` | Naive | `naive` |
| `hub` | `hub` | Chronos Bolt, Chronos T5, TTM, TimesFM | `chronos_bolt` |
| `chronos` | `chronos` | Chronos-2, plus hub | `chronos_2` |
| `granite` | `granite` | FlowState, plus hub | `flowstate` |
| `moirai` | `moirai` | Moirai, Lag-Llama, plus hub | `moirai_2` |
| `tirex` | `tirex` | TiRex, plus hub | `tirex` |
| `toto` | `toto` | Toto-2, plus hub | `toto_2_0_4m` |
| `mantis` | `mantis` | Mantis, plus hub | `mantis_8m` |
| `kronos` | `kronos` | Kronos, WindFM (not hub) | `kronos` |
| `full` | `full` | every family | `chronos_2` |

```bash
docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
```

Each family tag has a `-gpu` variant. There is no `:base-gpu`. `mantis` needs more than 127 rows of `past`. Names, checkpoints, and which families support multivariate, covariates, and quantiles: [catalog](https://tserve.readthedocs.io/en/latest/models/).

## Other ways to load a model

A checkpoint the catalog does not name:

```bash
tserve 'ttm-local=TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
```

A sktime `.zip` you already saved:

```bash
tserve --models-dir my-models custom-model-1 chronos_bolt
```

An estimator you built in Python, or `Server` instead of the CLI: [live objects](https://tserve.readthedocs.io/en/latest/server/live-objects/), [UV / Pip](https://tserve.readthedocs.io/en/latest/server/pip/).

## Where things are

After startup:

- Dashboard: <http://127.0.0.1:8000/>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

Guides: [server](https://tserve.readthedocs.io/en/latest/server/), [HTTP](https://tserve.readthedocs.io/en/latest/client/http/), [Python](https://tserve.readthedocs.io/en/latest/client/python/), [CLI](https://tserve.readthedocs.io/en/latest/reference/cli/), [errors](https://tserve.readthedocs.io/en/latest/reference/errors/), [development](https://tserve.readthedocs.io/en/latest/reference/development/).

## License

BSD 3-Clause. See [LICENSE](LICENSE).
