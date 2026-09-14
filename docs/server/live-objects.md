# Live objects

Registry ids cover published checkpoints. To serve an estimator you configured yourself, pass `(id, estimator)` pairs or `(id, craft spec)` pairs to [`Server`][fomo.server.serve.Server]. This is Python-only: `--load-models` takes catalog names, so live objects and craft specs have no CLI equivalent.

```python
from fomo.server import Server
from sktime.forecasting.chronos import ChronosForecaster

bolt = ChronosForecaster(
    model_path="amazon/chronos-bolt-mini",
    config={"device_map": "auto"},
)

Server(
    load_models=[
        "chronos-bolt",
        ("bolt-mini-local", bolt),
    ],
    host="127.0.0.1",
    port=8000,
).run()
```

The id is what predict requests send as `model`:

```json
{
  "models": [
    {"id": "chronos-bolt", "executor": "sktime", "source": "registry"},
    {"id": "bolt-mini-local", "executor": "sktime", "source": "object"}
  ]
}
```

## Craft specs

A craft spec is the same string you would pass to `sktime.registry.craft`. FoMo instantiates it at load time; predict still uses the id you chose, not the spec:

```python
from fomo.server import Server

Server(
    load_models=[
        "chronos-bolt",
        (
            "ttm-local",
            'TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="52-16-dec-52-r3", fit_strategy="zero-shot")',
        ),
    ],
    host="127.0.0.1",
    port=8000,
).run()
```

```json
{
  "models": [
    {"id": "chronos-bolt", "executor": "sktime", "source": "registry"},
    {"id": "ttm-local", "executor": "sktime", "source": "craft"}
  ]
}
```

The spec is evaluated only in your process when `Server` is constructed, never from an HTTP `model` field. A class name without parentheses (`"NaiveForecaster"`) is not an instance and is rejected. An empty spec raises `ValueError`. Passing a spec as a bare string in `load_models` is treated as an unknown registry id; wrap it as `(id, spec)`.

## Rules

- A live object must be an sktime `BaseForecaster`. A craft pair's second element must be a non-empty string. Anything else raises `TypeError` naming the id and the type you passed.
- Ids must be unique across the whole list. A collision — including with a registry id — raises `ValueError` before the second load.
- Registry ids, live objects, craft specs, and [saved models](models-dir.md) mix freely in one `load_models` list.
- The estimator's own dependencies have to be installed; FoMo only adds the ones its [extras](../models/index.md#dependencies) declare.

## Configured Hub estimators

The same mechanism serves a checkpoint or revision the registry does not name, either as a live object or as a craft spec:

```python
from fomo.server import Server
from sktime.forecasting.ttm import TinyTimeMixerForecaster

ttm = TinyTimeMixerForecaster(
    model_path="ibm-granite/granite-timeseries-ttm-r3",
    revision="52-16-dec-52-r3",
    fit_strategy="zero-shot",
)

Server(
    load_models=["chronos-bolt", ("ttm-local", ttm)],
    host="127.0.0.1",
    port=8000,
).run()
```

Each object or spec is loaded and warmed up like any other model, so startup pays the same download and warmup cost once. Registry ids and extras are on the [catalog](../models/index.md).
