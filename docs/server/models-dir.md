# Models from a directory

TServe serves estimators that sktime saved to disk, as `.zip` files. That is how a model you fitted or configured elsewhere reaches a server you start from the CLI or from a container.

## Save a model

`save()` appends the extension, and the directory has to exist first:

```python
from pathlib import Path

from sktime.forecasting.chronos import ChronosForecaster

Path("my-models").mkdir(exist_ok=True)
model = ChronosForecaster(model_path="amazon/chronos-bolt-tiny")
model.save("my-models/custom-model-1")
# writes my-models/custom-model-1.zip
```

A directory of saved models then looks like this:

```text
my-models/
├── custom-model-1.zip
├── custom-model-2.zip
└── custom-model-3.zip
```

## Load them

Point `--models-dir` at the directory, then name the file stems in `--model` or as leftover positionals:

=== "uv"

    ```bash
    uv run tserve serve --models-dir my-models --model custom-model-1 chronos-bolt
    ```

=== "pip"

    ```bash
    tserve serve --models-dir my-models --model custom-model-1 chronos-bolt
    ```

In Docker, mount the directory and use the container path:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" geetu040/tserve:hub --models-dir /models --model custom-model-1 chronos-bolt
```

Either way `custom-model-1` is served from the zip and `chronos-bolt`
from the registry, and `GET /models` labels them apart:

```json
{
  "models": [
    {"id": "naive", "executor": "sktime", "source": "registry"},
    {"id": "custom-model-1", "executor": "sktime", "source": "directory"},
    {"id": "chronos-bolt", "executor": "sktime", "source": "registry"}
  ]
}
```

## Rules

- `--models-dir` never loads a directory wholesale. It only rewrites models that are already in `--model` (or leftover positionals) and match a `.zip` stem in that directory.
- A name that matches no file falls through to the registry, and fails there if it is not a registry model.
- Other suffixes raise `ValueError`; a saved `.pkl` is not accepted.
- The directory itself has to exist.
- Dependencies are your problem: a saved TTM still needs the `hub` [extra](../models/index.md#dependencies) in the environment doing the loading.

## From Python

[`Server`][tserve.server.serve.Server] takes the same `models_dir` argument:

```python
from tserve.server import Server

Server(
    models_dir="my-models",
    model=["custom-model-1", "chronos-bolt"],
    host="127.0.0.1",
    port=8000,
).run()
```

A `pathlib.Path` in `model` also works on its own, no `models_dir` needed. The model is the file stem:

```python
from pathlib import Path

Server(model=[Path("my-models/custom-model-1.zip")], port=8000).run()
```

To serve an estimator that is already in memory, skip the file entirely — see [Live objects](live-objects.md). To pass a sktime craft spec instead of a zip, see [Craft specs](craft-specs.md).
