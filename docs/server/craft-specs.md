# Craft specs

A craft spec is the same string you would pass to `sktime.registry.craft`: a class call, including constructor kwargs, with no imports. Pass it to [`Server`][fomo.server.serve.Server] as `(id, spec)`, or to `fomo serve` as `id=spec`. Predict uses the **id**, not the spec string.

Catalog ids cover published checkpoints. A spec is how you load a checkpoint, revision, or configuration the [catalog](../models/index.md) does not name.

```python
from fomo.server import Server

Server(
    model=[
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

## From the command line

`--model` and leftover positionals split each token on the first `=`. Catalog ids have no `=`; everything after the first `=` is the spec, so kwargs may contain `=` too. Quote the whole token so constructor quotes survive the shell:

```bash
fomo serve --model chronos-bolt \
  'ttm-local=TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
```

Docker is the same argv after the image name. A token that looks like `ClassName(...)` with no `id=` is rejected; wrap it as `id=spec`. Flag details: [CLI](../reference/cli.md).

## Rules

- The spec must be a non-empty string that `craft` turns into a sktime `BaseForecaster` **instance**. A class name without parentheses (`"NaiveForecaster"`) is rejected.
- A bare spec in Python `model` is treated as an unknown registry id. Wrap it as `(id, spec)`.
- Ids must be unique across the whole list. A collision — including with a registry id — raises `ValueError` before the second load.
- Registry ids, [live objects](live-objects.md), craft specs, and [saved models](models-dir.md) mix freely in one `model` list.
- The estimator's own dependencies have to be installed; FoMo only adds the ones its [extras](../models/index.md#dependencies) declare.
- The spec is evaluated only in your process at startup, never from an HTTP `model` field.

Each spec is loaded and warmed up like any other model, so startup pays the download and warmup cost once.
