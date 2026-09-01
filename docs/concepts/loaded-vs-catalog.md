# Loaded vs catalog

Two lists that look similar and are not the same:

- **Catalog** — ids the server *can* load (`naive`, `chronos-2`, …) from [`SKTIME_REGISTRY`][fomo.runtime.registry.sktime_registry.SKTIME_REGISTRY]. See [Model catalog](../reference/catalog.md).
- **Loaded** — what [`bootstrap(load_models)`][fomo.runtime.bootstrap.bootstrap] / `--load-models` actually instantiated. `GET /models` and [`Client.models()`][fomo.client.client.Client.models] return only this list ([`ModelsResult`][fomo.types.models.ModelsResult]).

Nothing in the catalog is loaded until you select it. An empty server returns `"models": []`. A forecast `model` field must be a **loaded id**, not an executor name (`sktime`, …) and not a catalog id that this process never loaded.

[`Scheduler.run`][fomo.scheduling.scheduler.Scheduler.run] looks up `request.model` in the loaded-executors dict. A miss raises `RuntimeError`: `model {id!r} is not loaded on this server (loaded: …)` with comma-separated `repr` of sorted loaded ids, or `none` if none are loaded. JSON `POST /forecast` wraps that as HTTP 400.

Each listing row is [`ModelInfo`][fomo.types.models.ModelInfo]:

| field | |
| --- | --- |
| `id` | loaded model id used in forecast requests |
| `executor` | plugin that loaded the artifact: `sktime`, `pytorch-forecasting`, or `custom` |
| `source` | how [`resolve_model`][fomo.runtime.registry.resolver.resolve_model] obtained it: `registry`, `directory`, or `object` |
