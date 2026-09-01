# Extras and Hub weights

Install extras to match what the process will load. Names are `[project.optional-dependencies]` in `pyproject.toml`. See [Installation](../getting-started/installation.md) for the full table.

| you want | extra |
| --- | --- |
| Python [`Client`][fomo.client.client.Client] only | `client` |
| `fomo serve` / [`Server`][fomo.server.serve.Server] | `server` |
| registry id `naive` | `server` + `sktime-lite` (or `sktime`) |
| other registry ids (Hub checkpoints) | `server` + `sktime` |

`naive` is a `NaiveForecaster` and does not download weights. Every other catalog id's craft spec points at a Hugging Face (or equivalent) path. The first [`load`][fomo.runtime.executors.sktime.executor.SktimeExecutor.load] of that id pulls the checkpoint into the local Hub cache (`sktime.registry.craft`).

The Docker image always installs `server` and `sktime-lite`. Add Hub deps at build time:

```bash
docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
docker run --rm -p 8000:8000 fomo:sktime --load-models naive flowstate
```

Missing executor extras raise `ImportError` at [`create_executor`][fomo.runtime.executors.plugins.create_executor] telling you to install `fomo[{name}]`. The `pytorch-forecasting` extra exists; [`PytorchForecastingExecutor`][fomo.runtime.executors.pytorch_forecasting.executor.PytorchForecastingExecutor] raises `NotImplementedError` on `load` / `warmup` / `predict`.

A custom executor is a subclass of [`Executor`][fomo.runtime.executors.base.Executor] registered with [`@register`][fomo.runtime.executors.plugins.register]. Built-in names in [`available_executors`][fomo.runtime.executors.plugins.available_executors] are `sktime` and `pytorch-forecasting`. Those names are not registry model ids.
