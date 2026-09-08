# Load models

The registry is the list of ids the server *can* load. Nothing in it is loaded until `--load-models` / `load_models` selects it. `GET /models` is the loaded list, not the [catalog](catalog.md).

Do not invent ids. Forecast `model` must be a loaded id, not an executor name (`sktime`) and not a catalog id this process never loaded.

`naive` is `NaiveForecaster` — no Hub download. Every other id pulls a Hugging Face (or equivalent) checkpoint on first load. That needs the matching [family extra](../server/index.md#dependencies), or a Docker tag that already baked it in.

## Which extra / image?

| extra / image tag | estimator families | example ids |
| --- | --- | --- |
| `server` / `:base` | `NaiveForecaster` | `naive` |
| `hub` / `:hub` | Chronos Bolt/T5, TTM, TimesFM 2.x | `chronos-bolt-tiny`, `ttm-r3-512-30`, `timesfm-2.5` |
| `chronos` / `:chronos` | Chronos-2 | `chronos-2`, `chronos-2-small` |
| `kronos` / `:kronos` | Kronos, WindFM | `kronos`, `windfm` |
| `granite` / `:granite` | FlowState | `flowstate`, `flowstate-granite` |
| `moirai` / `:moirai` | Moirai, Lag-Llama | `moirai-2`, `lagllama` |
| `tirex` / `:tirex` | TiRex | `tirex` |
| `toto` / `:toto` | Toto-2 | `toto-2.0-4m` |
| `mantis` / `:mantis` | Mantis | `mantis-8m` |
| `full` / `:full` | all of the above | |

`kronos` is layered on `base`, not on `hub`. First Hub download is faster with `HF_TOKEN` set (a read token is enough). Mount `~/.cache/huggingface` in Docker so weights persist.

## Loading registered models

These ids are in the registry. Pick them with `--load-models`:

| id | estimator | id | estimator |
| --- | --- | --- | --- |
| `naive` | `NaiveForecaster` | `chronos-2` | `Chronos2Forecaster` |
| `chronos-bolt-tiny` | `ChronosForecaster` | `kronos` | `KronosForecaster` |
| `moirai-2` | `Moirai2Forecaster` | `ttm-r3-52-16` | `TinyTimeMixerForecaster` |
| `timesfm-2.5` | `TimesFM2Forecaster` | `toto-2.0-4m` | `Toto2Forecaster` |
| `flowstate` | `FlowStateForecaster` | `tirex` | `TiRexForecaster` |
| `windfm` | `WindFMForecaster` | `lagllama` | `LagLlamaForecaster` |
| `mantis-8m` | `MantisForecaster` | | |

Each family has more sizes and revisions; the [full catalog](catalog.md) lists every id.

```bash
fomo serve --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

First start of a Hub model downloads weights and runs a tiny warmup `fit` / `predict`. Then:

```bash
curl -s http://127.0.0.1:8000/models
```

```json
{
  "models": [
    {"id": "naive", "executor": "sktime", "source": "registry"},
    {"id": "chronos-bolt-tiny", "executor": "sktime", "source": "registry"},
    {"id": "ttm-r3-512-30", "executor": "sktime", "source": "registry"}
  ]
}
```

`source` is `registry`, `directory`, or `object`. Duplicate ids raise `ValueError` before a second load.

Asking for an id that is not loaded is HTTP 400:

```text
model 'timesfm-2.5' is not loaded on this server (loaded: 'chronos-bolt-tiny', 'naive', 'ttm-r3-512-30')
```

## Loading models from a directory

Saved sktime **`.zip`** files (not `.pkl`). `--models-dir` does not auto-load the directory. Only stems already named in `--load-models` are rewritten to paths.

```
my-models/
├── custom-model-1.zip
├── custom-model-2.zip
└── custom-model-3.zip
```

From source:

```bash
fomo serve --models-dir my-models --load-models custom-model-1 custom-model-2
```

If `my-models/custom-model-1.zip` exists, that id loads from the zip (`source="directory"`) instead of the registry. Other suffixes raise `ValueError`.

Mount the same directory into Docker and point `--models-dir` at the container path:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" geetu040/fomo:hub --models-dir /models --load-models custom-model-1 custom-model-2
```

You can mix zip stems with registry ids:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" geetu040/fomo:hub --models-dir /models --load-models custom-model-1 naive chronos-bolt-tiny
```

## Loading live objects

SDK only. The object must be a sktime `BaseForecaster`:

```python
from fomo.server import Server
from sktime.forecasting.chronos import ChronosForecaster
from sktime.forecasting.ttm import TinyTimeMixerForecaster

bolt = ChronosForecaster(model_path="amazon/chronos-bolt-tiny")
ttm = TinyTimeMixerForecaster(
    model_path="ibm-granite/granite-timeseries-ttm-r3",
    revision="52-16-dec-52-r3",
    fit_strategy="zero-shot",
)

Server(
    load_models=[
        ("chronos-bolt-tiny", bolt),
        ("ttm-local", ttm),
        "naive",
    ],
    host="127.0.0.1",
    port=8000,
).run()
```

`source` is `"object"` for the tuples. Mix registry ids and tuples in the same list.

## Start a server with some models

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

From source (needs the `hub` extra, or another family extra that includes those ids):

```bash
uv run fomo serve --host 0.0.0.0 --port 8000 --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Swap `model` on a [forecast](../client/http.md) between those loaded ids. `naive` is a drift forecast and needs no download — use it to check the pipe, then switch to a Hub id.

Some ids need a longer history than a 5-row toy series. `mantis-8m` requires more observations than its `context_length` (127).

The [catalog](catalog.md) lists every registry id.
