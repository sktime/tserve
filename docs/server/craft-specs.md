# Craft specs

A craft spec is the same string you would pass to `sktime.registry.craft`: a class call, including constructor kwargs, with no imports. Pass it to [`Server`][tserve.server.serve.Server] as `(id, spec)`, or to `tserve` as `id=spec`. Predict uses that name as `model`, not the spec string.

Catalog models cover published checkpoints. A spec is how you load a checkpoint, revision, or configuration the [catalog](../models/index.md) does not name.

```python
from tserve.server import Server

Server(
    model=[
        "chronos_bolt",
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
    {"id": "naive", "executor": "sktime", "source": "registry"},
    {"id": "chronos_bolt", "executor": "sktime", "source": "registry"},
    {"id": "ttm-local", "executor": "sktime", "source": "craft"}
  ]
}
```

## From the command line

Leftover positionals split each token on the first `=`. Catalog models have no `=`; everything after the first `=` is the spec, so kwargs may contain `=` too. Quote the whole token so constructor quotes survive the shell:

```bash
tserve chronos_bolt \
  'ttm-local=TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
```

Docker is the same argv after the image name. A token that looks like `ClassName(...)` with no `id=` is rejected; wrap it as `id=spec`. Flag details: [CLI](../reference/cli.md).

## Rules

- The spec must be a non-empty string that `craft` turns into a sktime `BaseForecaster` **instance**. A class name without parentheses (`"NaiveForecaster"`) is rejected.
- A bare spec in Python `model` is treated as an unknown registry model. Wrap it as `(id, spec)`.
- Models must be unique across the whole list. A collision — including with a registry model — raises `ValueError` before the second load.
- Registry models, [live objects](live-objects.md), craft specs, and [saved models](models-dir.md) mix freely in one `model` list.
- The estimator's own dependencies have to be installed; TServe only adds the ones its [extras](../models/index.md#dependencies) declare.
- The spec is evaluated only in your process at startup, never from an HTTP `model` field.

Each spec is loaded and warmed up like any other model, so startup pays the download and warmup cost once.
