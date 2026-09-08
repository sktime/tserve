# Python

[`Client`][fomo.client.client.Client] talks to a running server. It coerces locally and posts Arrow to `/forecast/bytes`. JSON `POST /forecast` is documented under [HTTP](http.md); the fields are the same.

## Install

On a machine that only calls a remote server, from a clone (FoMo is **not on PyPI yet**):

=== "uv"

    ```bash
    uv sync --extra client
    ```

=== "pip"

    ```bash
    pip install -e ".[client]"
    ```

If you already installed the server extras in the same environment, add `client` as well (`uv sync --extra server --extra client` or `pip install -e ".[server,client]"`). The `client` extra pulls `httpx2`.

## Connect

Construct a client, call it, then close the session:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
print(client.health())  # status='ok' error=None
print(client.models())  # loaded ids only
print(client.stats())
client.close()
```

`with Client(...)` also closes the session for you:

```python
from fomo.client import Client

with Client("http://127.0.0.1:8000", timeout=120.0) as client:
    print(client.models())
```

Default timeout is 60s. Hub models can need longer — pass `timeout=` as above.

`client.health()` / `.models()` / `.stats()` wrap the three JSON GETs. HTTP status >= 400 becomes `RuntimeError` with the server `error` message. Connection and timeout errors are `httpx.RequestError`. See [Errors](../reference/errors.md).

## Forecast

Same fields as [HTTP request fields](http.md#request-fields). **Whatever you pass as `past` is what `predictions` / `quantiles` come back as.**

Examples below use `chronos-bolt-tiny`, matching the [server](server.md) walkthrough (`--load-models naive chronos-bolt-tiny ttm-r3-512-30`). Swap `model` for any other loaded id.

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
result = client.forecast(
    past={
        "timestamp": [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ],
        "sales": [120, 135, 128, 142, 138],
    },
    time="timestamp",
    target=["sales"],
    fh=3,
    model="chronos-bolt-tiny",
)
print(result.predictions)
client.close()
# {'timestamp': [Timestamp('2024-01-06 00:00:00'), …],
#  'sales': [139.96…, 138.93…, 138.26…]}
```

Row-matrix in → row-matrix out:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
result = client.forecast(
    past={
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-01", 120],
            ["2024-01-02", 135],
            ["2024-01-03", 128],
            ["2024-01-04", 142],
            ["2024-01-05", 138],
        ],
    },
    time="timestamp",
    target=["sales"],
    fh=3,
    model="chronos-bolt-tiny",
)
print(result.predictions)
client.close()
# {'columns': ['timestamp', 'sales'],
#  'data': [[Timestamp('2024-01-06 00:00:00'), 139.96…], …]}
```

You can omit `time` and `target` when the first column is time and the rest are targets:

```python
result = client.forecast(past=past, fh=3, model="chronos-bolt-tiny")
```

## Data format

JSON shapes are in [HTTP](http.md#data-format). The Python client also takes pandas, polars, pyarrow, and Narwhals.

Snippets below assume a connected client:

```python
from fomo.client import Client

client = Client("http://127.0.0.1:8000")
```

**pandas** — see [covariates](#covariates) and [sktime](#sktime-and-indexed-frames).

**polars** — see [quantiles](#quantiles). Requires `pip install polars` (the `polars` package, not a FoMo extra).

**pyarrow** Table:

```python
import pyarrow as pa

past = pa.table(
    {
        "timestamp": [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ],
        "sales": [120.0, 135.0, 128.0, 142.0, 138.0],
    }
)
result = client.forecast(
    past=past, time="timestamp", target=["sales"], fh=3, model="chronos-bolt-tiny"
)
type(result.predictions)  # pyarrow.Table
```

**Narwhals** (stays Narwhals, same backend as `past`):

```python
import narwhals as nw
import pandas as pd

past = nw.from_native(
    pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "sales": [120, 135, 128, 142, 138],
        }
    )
)
result = client.forecast(
    past=past, time="timestamp", target=["sales"], fh=3, model="chronos-bolt-tiny"
)
type(result.predictions)  # narwhals.DataFrame
```

## sktime and indexed frames

FoMo does not read a pandas/sktime index as the time axis. Time must be a **column**. `load_airline()` is a Series with a `PeriodIndex`; passing it (or `to_frame()` without `reset_index()`) fails because there is no time column and inferred `target` is empty.

```python
from sktime.datasets import load_airline
from fomo.client import Client

past = load_airline().to_frame("passengers").reset_index()
past = past.rename(columns={"Period": "timestamp"})
past["timestamp"] = past["timestamp"].astype(str)

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past=past, time="timestamp", target=["passengers"], fh=3, model="chronos-bolt-tiny"
    )
    print(result.predictions)
```

Panel and hierarchical sktime mtypes are not supported.

## Covariates

`static` is one row, broadcast over time as exogenous `X`. `future` is optional; when `static` is set it supplies the future **index** (must include `time`). Extra columns on `past` / `future` are accepted on the wire; the current sktime converter does not map them onto `X` — only the first `static` row is broadcast.

pandas in → pandas out:

```python
import pandas as pd
from fomo.client import Client

past = pd.DataFrame(
    {
        "date": pd.date_range("2023-01-01", periods=12, freq="MS"),
        "sales": [120, 135, 128, 142, 150, 161, 155, 168, 173, 181, 195, 210],
        "price": [
            9.99,
            9.49,
            9.99,
            8.99,
            9.99,
            8.49,
            9.99,
            8.99,
            9.49,
            9.99,
            8.99,
            9.99,
        ],
        "promo": [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
    }
)
future = pd.DataFrame(
    {
        "date": pd.date_range("2024-01-01", periods=3, freq="MS"),
        "price": [8.99, 9.99, 9.49],
        "promo": [1, 0, 1],
    }
)
static = pd.DataFrame(
    {
        "store_type": ["urban"],
        "region": ["EU-west"],
        "floor_sqm": [420],
        "n_skus": [18],
    }
)

client = Client("http://127.0.0.1:8000", timeout=120.0)
result = client.forecast(
    past=past,
    future=future,
    static=static,
    time="date",
    target=["sales"],
    fh=3,
    model="chronos-bolt-tiny",
)
print(type(result.predictions))  # pandas.DataFrame
print(result.predictions)
client.close()
```

`target` can be a list of several columns if the loaded estimator accepts multivariate `y`.

## Quantiles

Add `quantiles=[0.1, 0.5, 0.9]`. Columns come back flattened: `{variable}_{alpha}` (for `naive`, `sales_0.1`, `sales_0.5`, `sales_0.9`). The estimator must implement `predict_quantiles`; Chronos Bolt (`chronos-bolt-tiny`) does not and the request fails, so this example uses loaded `naive`.

polars in → polars out. Install polars yourself (`pip install polars`); it is not a FoMo extra.

```python
import polars as pl
from fomo.client import Client

past = pl.DataFrame(
    {
        "month": [
            "2023-01-01",
            "2023-02-01",
            "2023-03-01",
            "2023-04-01",
            "2023-05-01",
            "2023-06-01",
            "2023-07-01",
            "2023-08-01",
            "2023-09-01",
            "2023-10-01",
            "2023-11-01",
            "2023-12-01",
        ],
        "sales": [120, 135, 128, 142, 150, 161, 155, 168, 173, 181, 195, 210],
    }
)

client = Client("http://127.0.0.1:8000", timeout=120.0)
result = client.forecast(
    past=past,
    time="month",
    target=["sales"],
    fh=3,
    quantiles=[0.1, 0.5, 0.9],
    model="naive",
)
print(type(result.predictions))  # polars.DataFrame
print(result.predictions)
print(result.quantiles)
client.close()
# predictions: month / sales ≈ 218.18, 226.36, 234.55
# quantiles columns: month, sales_0.1, sales_0.5, sales_0.9
```

`predictions` stays the point forecast. `quantiles` is a second table, or `null` / `None` when the field was omitted.
