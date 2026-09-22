# Python

[`Client`][tserve.client.client.Client] sends predictions to a running TServe server. It accepts native Python tables, converts them to Arrow, and posts to `/predict/bytes`.

## Methods

| call | what it gives you |
| --- | --- |
| `Client(url, timeout=60.0)` | [a client bound to one server](#connect) |
| `client.predict(past=..., fh=...)` | [a prediction](#send-a-prediction) as a `PredictResponse` |
| `client.health()` | process liveness |
| `client.models()` | loaded models |
| `client.stats()` | uptime, memory, per-model metrics |
| `client.close()` | closes the HTTP session |

`predict` returns `predictions`, `quantiles`, `model`, and `request_id`. Full signatures are in the [Python API reference](../reference/api.md).

## Start a server

The point forecast examples use `chronos_bolt`. Quantile examples use `timesfm_2_5`, whose estimator supports quantile prediction; Chronos Bolt does not:

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt timesfm_2_5
```

See [Server](../server/index.md) for Docker, UV / Pip, and server options. The client URL points to this process, not a hosted TServe API.

## Install

Install the `client` extra. Python 3.12 or newer is required.

=== "uv"

    ```bash
    uv pip install "tserve[client]"
    ```

=== "pip"

    ```bash
    pip install "tserve[client]"
    ```

The `client` extra is enough on a machine that only calls a server. Add `server` and the required [family extra](../models/index.md#dependencies) only when the same environment also runs the server.

## Connect

Use the client as a context manager so its HTTP session is closed:

```python
from tserve.client import Client

with Client("http://127.0.0.1:8000", timeout=120.0) as client:
    print(client.health())
    print(client.models())
    print(client.stats())
```

`models()` reports what this process loaded, not the registry [catalog](../models/index.md), so it is the quickest way to check which `model` values a prediction can use.

The default timeout is 60 seconds. Increase it for forecasts that need more time.

## Send a prediction

The method takes the same fields as JSON `POST /predict`. This example sends five days of sales and requests the next three:

```python
from tserve.client import Client

past = {
    "timestamp": [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
    ],
    "sales": [120, 135, 128, 142, 138],
}

with Client("http://127.0.0.1:8000") as client:
    result = client.predict(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="chronos_bolt",
    )

print(result.predictions)
print(result.model)
print(result.request_id)
```

`result.predictions` is a column dictionary because `past` was one:

```python
{
    "timestamp": [
        Timestamp("2024-01-06 00:00:00"),
        Timestamp("2024-01-07 00:00:00"),
        Timestamp("2024-01-08 00:00:00"),
    ],
    "sales": [139.96, 138.93, 138.26],
}
```

See [Data specification](data.md) for all fields, inference rules, and table constraints.

## Use native tables

`predictions` and `quantiles` use the same table type as `past`. The following examples send the same data in four native formats.

=== "pandas"

    ```python
    import pandas as pd
    from tserve.client import Client

    past = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "sales": [120, 135, 128, 142, 138],
        }
    )

    with Client("http://127.0.0.1:8000") as client:
        result = client.predict(
            past=past,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="chronos_bolt",
        )

    print(type(result.predictions))  # pandas.DataFrame
    ```

=== "polars"

    ```python
    import polars as pl
    from tserve.client import Client

    past = pl.DataFrame(
        {
            "timestamp": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "sales": [120, 135, 128, 142, 138],
        }
    )

    with Client("http://127.0.0.1:8000") as client:
        result = client.predict(
            past=past,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="chronos_bolt",
        )

    print(type(result.predictions))  # polars.DataFrame
    ```

=== "pyarrow"

    ```python
    import pyarrow as pa
    from tserve.client import Client

    past = pa.table(
        {
            "timestamp": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "sales": [120, 135, 128, 142, 138],
        }
    )

    with Client("http://127.0.0.1:8000") as client:
        result = client.predict(
            past=past,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="chronos_bolt",
        )

    print(type(result.predictions))  # pyarrow.Table
    ```

=== "Narwhals"

    ```python
    import narwhals as nw
    import pandas as pd
    from tserve.client import Client

    past = nw.from_native(
        pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
                "sales": [120, 135, 128, 142, 138],
            }
        ),
        eager_only=True,
    )

    with Client("http://127.0.0.1:8000") as client:
        result = client.predict(
            past=past,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="chronos_bolt",
        )

    print(type(result.predictions))  # narwhals.DataFrame
    ```

pandas and polars are not installed by the `client` extra. Install either package separately if you use it. pyarrow and Narwhals are core TServe dependencies.

## Use an indexed pandas frame

Time must be a column. Reset a pandas or sktime index before forecasting:

```python
from tserve.client import Client
from sktime.datasets import load_airline

past = load_airline().to_frame("passengers").reset_index()
past = past.rename(columns={"Period": "timestamp"})
past["timestamp"] = past["timestamp"].astype(str)

with Client("http://127.0.0.1:8000") as client:
    result = client.predict(
        past=past,
        time="timestamp",
        target=["passengers"],
        fh=3,
        model="chronos_bolt",
    )

print(result.predictions)
```

Panel and hierarchical sktime data are not supported.

## Request static data

Static values are supplied as a one-row table. A `future` table can provide the timestamps for the requested horizon. This example needs `chronos_2`, which supports covariates. Stop the starter server and restart with the `chronos` image:

```bash
docker run --rm -p 8000:8000 sktime/tserve:chronos chronos_2
```

```python
import pandas as pd
from tserve.client import Client

past = pd.DataFrame(
    {
        "month": pd.date_range("2024-01-01", periods=5, freq="MS"),
        "sales": [120, 135, 128, 142, 150],
    }
)
future = pd.DataFrame({"month": pd.date_range("2024-06-01", periods=3, freq="MS")})
static = pd.DataFrame({"store_type": ["urban"], "region": ["EU-west"]})

with Client("http://127.0.0.1:8000") as client:
    result = client.predict(
        past=past,
        future=future,
        static=static,
        time="month",
        target=["sales"],
        fh=3,
        model="chronos_2",
    )

print(result.predictions)
```

See [Future and static data](data.md#future-and-static-data) for the current executor behavior, including the limitation on time-varying covariates.

## Request quantiles

Add `quantiles` when the loaded estimator supports quantile prediction. This example uses the compatible `timesfm_2_5` model; Chronos Bolt and TTM do not support quantiles:

```python
from tserve.client import Client

past = {
    "month": [
        "2024-01-01",
        "2024-02-01",
        "2024-03-01",
        "2024-04-01",
        "2024-05-01",
    ],
    "sales": [120, 135, 128, 142, 150],
}

with Client("http://127.0.0.1:8000") as client:
    result = client.predict(
        past=past,
        time="month",
        target=["sales"],
        fh=3,
        model="timesfm_2_5",
        quantiles=[0.1, 0.5, 0.9],
    )

print(result.predictions)
print(result.quantiles)
```

`predictions` remains the point forecast. Many estimators name quantile columns `{target}_{level}` (`sales_0.1`, `sales_0.5`, `sales_0.9`). `timesfm_2_5` currently uses a positional prefix (`0_0.1`, `0_0.5`, `0_0.9`).

## Handle errors

Local request validation can raise Pydantic `ValidationError` before any HTTP call. Server responses with status 400 or higher become `RuntimeError`. Connection and timeout failures are `tserve.client.TransportError` (do not catch `httpx.RequestError` — TServe vendors `httpx2`).

See [Errors](../reference/errors.md) for the messages each case produces.
