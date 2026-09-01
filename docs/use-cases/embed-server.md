# Embed `Server`

Construct [`Server`][fomo.server.serve.Server] in-process instead of using the CLI. [`Server.__init__`][fomo.server.serve.Server] already runs [`bootstrap`][fomo.runtime.bootstrap.bootstrap] and builds the FastAPI app. [`run()`][fomo.server.serve.Server.run] starts uvicorn and blocks.

```python
from fomo.server import Server

server = Server(load_models=["naive"], host="127.0.0.1", port=8000)
print(server.url)  # http://127.0.0.1:8000
server.run()
```

Omitting `load_models` starts empty, same as a bare `fomo serve`. Pass a `(id, estimator)` pair to load an in-process sktime `BaseForecaster` (SDK only; the CLI still takes names):

```python
from fomo.server import Server
from sktime.forecasting.naive import NaiveForecaster

Server(
    load_models=[("naive", NaiveForecaster())],
    host="127.0.0.1",
    port=8000,
).run()
```

You can mix registry ids and objects:

```python
from fomo.server import Server
from sktime.forecasting.naive import NaiveForecaster

Server(
    load_models=["chronos-2", ("naive", NaiveForecaster())],
    host="127.0.0.1",
    port=8000,
).run()
```

The object must be a sktime `BaseForecaster`; otherwise [`resolve_model`][fomo.runtime.registry.resolver.resolve_model] raises `TypeError`. Duplicate loaded ids raise `ValueError`.

`server.app` is the FastAPI app if you want to mount it or pass it to uvicorn yourself:

```python
import uvicorn
from fomo.server import Server

server = Server(load_models=["naive"], host="127.0.0.1", port=8000)
# uvicorn.run(server.app, host=server.host, port=server.port, log_level=server.log_level)
server.run()
```

Forecast `request.model` must be a **loaded id**. See [Load models](../how-to/load-models.md) and [`Server`][fomo.server.serve.Server] in the [API reference](../reference/api.md#fomo.server.serve.Server).
