# Live objects

Registry models cover published checkpoints. To serve an estimator you configured yourself, pass `(id, estimator)` pairs to [`Server`][fomo.server.serve.Server]. This is Python-only: `--model` takes names, so a live object has no CLI equivalent. For a spec string instead of an instance, see [Craft specs](craft-specs.md).

```python
from fomo.server import Server
from sktime.forecasting.chronos import ChronosForecaster

bolt = ChronosForecaster(
    model_path="amazon/chronos-bolt-mini",
    config={"device_map": "auto"},
)

Server(
    model=[
        "chronos-bolt",
        ("bolt-mini-local", bolt),
    ],
    host="127.0.0.1",
    port=8000,
).run()
```

That name is what predict requests send as `model`:

```json
{
  "models": [
    {"id": "naive", "executor": "sktime", "source": "registry"},
    {"id": "chronos-bolt", "executor": "sktime", "source": "registry"},
    {"id": "bolt-mini-local", "executor": "sktime", "source": "object"}
  ]
}
```

## Rules

- The object must be an sktime `BaseForecaster`. Anything else raises `TypeError` naming the model and the type you passed.
- Models must be unique across the whole list. A collision — including with a registry model — raises `ValueError` before the second load.
- Registry models, live objects, [craft specs](craft-specs.md), and [saved models](models-dir.md) mix freely in one `model` list.
- The estimator's own dependencies have to be installed; FoMo only adds the ones its [extras](../models/index.md#dependencies) declare.

## Configured Hub estimators

The same mechanism serves a checkpoint or revision the registry does not name:

```python
from fomo.server import Server
from sktime.forecasting.ttm import TinyTimeMixerForecaster

ttm = TinyTimeMixerForecaster(
    model_path="ibm-granite/granite-timeseries-ttm-r3",
    revision="52-16-dec-52-r3",
    fit_strategy="zero-shot",
)

Server(
    model=["chronos-bolt", ("ttm-local", ttm)],
    host="127.0.0.1",
    port=8000,
).run()
```

Each object is loaded and warmed up like any other model, so startup pays the same download and warmup cost once. Registry models and extras are on the [catalog](../models/index.md). The same checkpoint as a spec string: [Craft specs](craft-specs.md).
