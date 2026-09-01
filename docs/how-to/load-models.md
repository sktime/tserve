# Load models

Three ways to get a loaded id. `GET /models` and [`Client.models()`][fomo.client.client.Client.models] list **loaded** ids only, not the [catalog](../reference/catalog.md). Each listing row is [`ModelInfo`][fomo.types.models.ModelInfo]: `id`, `executor`, `source`.

[`resolve_model`][fomo.runtime.registry.resolver.resolve_model] currently always sets `executor="sktime"` for registry ids, `.zip` paths, and `(id, BaseForecaster)` tuples. [`bootstrap`][fomo.runtime.bootstrap.bootstrap] then [`create_executor`][fomo.runtime.executors.plugins.create_executor], [`load`][fomo.runtime.executors.base.Executor.load], [`warmup`][fomo.runtime.executors.base.Executor.warmup], and [`stats.register`][fomo.logging.stats.Stats]. Duplicate `ModelInfo.id` values raise `ValueError` before a second load.

## Registry ids

String names in `--load-models` / `load_models` look up [`SKTIME_REGISTRY`][fomo.runtime.registry.sktime_registry.SKTIME_REGISTRY]. Unknown ids raise `ValueError` listing known keys. `naive` is `NaiveForecaster()` (no Hub download). Other catalog specs point at Hugging Face (or equivalent) checkpoints; first load pulls weights.

```bash
fomo serve --load-models naive
# Hub example (needs the sktime extra):
# fomo serve --load-models flowstate
```

`source` on `GET /models` is `"registry"`. After load, [`SktimeExecutor.warmup`][fomo.runtime.executors.sktime.executor.SktimeExecutor.warmup] fits a dummy 3-row `y` and predicts `fh=[1]`.

## `--models-dir` zip stems

When `models_dir` is set, [`Server`][fomo.server.serve.Server] lists that directory. For each path whose **stem** is already in `load_models`, it replaces that string id with the `pathlib.Path`. [`resolve_model`][fomo.runtime.registry.resolver.resolve_model] then treats a `Path` as a saved sktime **`.zip`** (`source="directory"`, id = stem). Other suffixes raise `ValueError`. Existence is not checked at resolve time; [`SktimeExecutor.load`][fomo.runtime.executors.sktime.executor.SktimeExecutor.load] calls `sktime.base.load`.

The directory is not loaded wholesale. Only stems already named in `--load-models` / `load_models` are rewritten. `.pkl` files are not rewritten into loadable artifacts.

```bash
fomo serve --models-dir /path/to/zips --load-models my-forecaster
```

If `/path/to/zips/my-forecaster.zip` exists, that entry loads from the zip instead of the registry.

## SDK `(id, estimator)`

CLI still takes names. The [`Server`][fomo.server.serve.Server] constructor also accepts a `(id, estimator)` pair. The object must be a sktime `BaseForecaster`; otherwise [`resolve_model`][fomo.runtime.registry.resolver.resolve_model] raises `TypeError`. `source` is `"object"`.

```python
from fomo.server import Server
from sktime.forecasting.naive import NaiveForecaster

Server(load_models=[("naive", NaiveForecaster())]).run()
```

Forecast `model` must be one of those loaded ids, not an executor name (`sktime`) and not a catalog id this process never loaded. See [Loaded vs catalog](../concepts/loaded-vs-catalog.md).
