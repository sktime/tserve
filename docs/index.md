# FoMo

FoMo is a time-series foundation-model inference server. Load selected models once, keep them warm, and forecast over HTTP or the Python [`Client`][fomo.client.client.Client]. It is not a training library.

Nothing is loaded by default. A bare `fomo serve` or [`Server()`][fomo.server.serve.Server] starts with an empty model list. Name registry ids with `--load-models` / `load_models` to load them. `GET /models` and [`Client.models()`][fomo.client.client.Client.models] list only what this process loaded, not the full [catalog](reference/catalog.md).

The Docker image is different: its `CMD` loads `naive`. That is an image default, not the Python default.

Once the process is up:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

There is no hosted FoMo API and no authentication. Every URL is the process you started.

Start with [Installation](getting-started/installation.md) and [Quickstart](getting-started/quickstart.md). Field semantics live on [`ForecastRequest`][fomo.types.models.ForecastRequest]; the generated signatures are in the [API reference](reference/api.md).
