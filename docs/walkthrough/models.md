# Models

The registry is the list of ids the server *can* load. Nothing in it is loaded until `--load-models` / `load_models` selects it. `GET /models` is the loaded list, not this catalog.

Do not invent ids. Forecast `model` must be a loaded id, not an executor name (`sktime`) and not a catalog id this process never loaded.

`naive` is `NaiveForecaster` — no Hub download. Every other id pulls a Hugging Face (or equivalent) checkpoint on first load. That needs the `sktime` extra, or the [`geetu040/fomo:sktime`](docker.md) image.

## Loading registered models

These ids are in the registry. Pick them with `--load-models`:

| id | estimator | id | estimator |
| --- | --- | --- | --- |
| `naive` | `NaiveForecaster` | `chronos-2` | `Chronos2Forecaster` |
| `chronos-bolt-tiny` | `ChronosForecaster` | `kronos` | `KronosForecaster` |
| `moirai-2` | `Moirai2Forecaster` | `ttm-r3-52-16` | `TinyTimeMixerForecaster` |
| `timesfm-2.5` | `TimesFM2Forecaster` | `toto-2.0-4m` | `Toto2Forecaster` |
| `flowstate` | `FlowStateForecaster` | `tirex` | `TiRexForecaster` |
| `windfm` | `WindFMForecaster` | `aurora` | `AuroraForecaster` |
| `lagllama` | `LagLlamaForecaster` | `falconx` | `FalconXForecaster` |
| `mantis-8m` | `MantisForecaster` | | |

Each family has more sizes and revisions; the [full catalog](#full-catalog) is below.

```bash
fomo serve --load-models naive chronos-2 timesfm-2.5
```

First start of a Hub model downloads weights and runs a tiny warmup `fit` / `predict`. Then:

```bash
curl -s http://127.0.0.1:8000/models
# {"models":[
#   {"id":"naive","executor":"sktime","source":"registry"},
#   {"id":"chronos-2","executor":"sktime","source":"registry"},
#   {"id":"timesfm-2.5","executor":"sktime","source":"registry"}
# ]}
```

`source` is `registry`, `directory`, or `object`. Duplicate ids raise `ValueError` before a second load.

## Loading models from a directory

Saved sktime **`.zip`** files (not `.pkl`). `--models-dir` does not auto-load the directory. Only stems already named in `--load-models` are rewritten to paths.

```
my-models/
├── custom-model-1.zip
├── custom-model-2.zip
└── custom-model-3.zip
```

```bash
fomo serve --models-dir my-models --load-models custom-model-1 custom-model-2
```

If `my-models/custom-model-1.zip` exists, that id loads from the zip (`source="directory"`) instead of the registry. Other suffixes raise `ValueError`.

## Loading live objects

SDK only. The object must be a sktime `BaseForecaster`:

```python
from fomo.server import Server
from sktime.forecasting.chronos import ChronosForecaster

model = ChronosForecaster(model_path="amazon/chronos-bolt-tiny")

Server(
    load_models=[
        ("chronos-bolt-tiny", model),
        "timesfm-2.5",
    ],
    host="127.0.0.1",
    port=8000,
).run()
```

`source` is `"object"`. Mix registry ids and tuples in the same list.

## Start a server with some models

For a local walkthrough, `naive` plus two Hub models on the sktime image:

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive timesfm-2.5 chronos-2
```

From source (needs the `sktime` extra):

```bash
uv run fomo serve --host 0.0.0.0 --port 8000 \
  --load-models naive timesfm-2.5 chronos-2
```

Swap `model` on a [forecast](client.md) between those loaded ids. `naive` repeats a drift forecast and needs no download — use it to check the pipe, then switch to `chronos-2` / `timesfm-2.5`.

## Full catalog

Ids the server can load. TTM ids are `{revision}-{context}-{horizon}`, with optional `-lite` / `-l1`.

**Baseline**

| id | estimator |
| --- | --- |
| `naive` | `NaiveForecaster` |

**Chronos**

| id | estimator |
| --- | --- |
| `chronos-2`, `chronos-2-small`, `chronos-2-synth` | `Chronos2Forecaster` |
| `chronos-bolt-tiny`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` | `ChronosForecaster` |
| `chronos-t5-tiny`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` | `ChronosForecaster` |

**Kronos / WindFM**

| id | estimator |
| --- | --- |
| `kronos`, `kronos-mini`, `kronos-base` | `KronosForecaster` |
| `windfm`, `windfm-robust` | `WindFMForecaster` |

**Moirai**

| id | estimator |
| --- | --- |
| `moirai-2` | `Moirai2Forecaster` |
| `moirai-1.0-r-small`, `moirai-1.0-r-base`, `moirai-1.0-r-large` | `MOIRAIForecaster` |
| `moirai-1.1-r-small`, `moirai-1.1-r-base`, `moirai-1.1-r-large` | `MOIRAIForecaster` |

**TimesFM / Toto / FlowState / TiRex**

| id | estimator |
| --- | --- |
| `timesfm-2.5`, `timesfm-2` | `TimesFM2Forecaster` |
| `toto-2.0-4m`, `toto-2.0-22m`, `toto-2.0-313m`, `toto-2.0-1b`, `toto-2.0-2.5b` | `Toto2Forecaster` |
| `flowstate`, `flowstate-granite` | `FlowStateForecaster` |
| `tirex`, `tirex-1.1-gifteval` | `TiRexForecaster` |

**TTM** (`TinyTimeMixerForecaster`)

- r1: `ttm-r1-512-96`, `ttm-r1-1024-96`
- r2: `ttm-r2-512-96`, `ttm-r2-512-192`, `ttm-r2-512-336`, `ttm-r2-512-720`, `ttm-r2-1024-96`, `ttm-r2-1024-192`, `ttm-r2-1024-336`, `ttm-r2-1024-720`, `ttm-r2-1536-96`, `ttm-r2-1536-192`, `ttm-r2-1536-336`, `ttm-r2-1536-720`
- r2.1: `ttm-r2.1-52-16`, `ttm-r2.1-52-16-l1`, `ttm-r2.1-90-30`, `ttm-r2.1-90-30-l1`, `ttm-r2.1-512-48`, `ttm-r2.1-512-48-l1`, `ttm-r2.1-512-96`, `ttm-r2.1-512-96-l1`, `ttm-r2.1-180-60-l1`, `ttm-r2.1-360-60-l1`
- r3: `ttm-r3-52-16`, `ttm-r3-90-30`, `ttm-r3-156-16`, `ttm-r3-180-60`, `ttm-r3-360-60`, `ttm-r3-512-30`, `ttm-r3-512-48`, `ttm-r3-512-96`, `ttm-r3-512-336`, `ttm-r3-768-48`, `ttm-r3-1024-48`, `ttm-r3-1024-96`, `ttm-r3-1024-720`, `ttm-r3-1536-96`, `ttm-r3-1536-720`, `ttm-r3-2048-96`, `ttm-r3-2048-720`, `ttm-r3-2560-96`, `ttm-r3-2560-720`, `ttm-r3-3072-96`, `ttm-r3-3072-720` — each also has a `-lite` sibling (`ttm-r3-52-16-lite`, …)

**Other**

| id | estimator |
| --- | --- |
| `aurora` | `AuroraForecaster` |
| `lagllama` | `LagLlamaForecaster` |
| `falconx` | `FalconXForecaster` |
| `mantis`, `mantis-8m`, `mantis-plus` | `MantisForecaster` |

FoMo does not ship a capability matrix. Quantile support is the estimator's `predict_quantiles`; there is no FoMo flag. Asking an id that cannot return quantiles fails the request.
