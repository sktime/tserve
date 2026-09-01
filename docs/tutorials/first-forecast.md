# First forecast

Pandas in, pandas out. The server must already be running with `naive` loaded. See [Quickstart](../getting-started/quickstart.md).

```python
import pandas as pd
from fomo.client import Client

past = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "sales": [120, 135, 128, 142, 138],
    }
)

with Client("http://127.0.0.1:8000") as client:
    print(client.health())
    print(client.models())
    result = client.forecast(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
    )

print(type(result.predictions))  # pandas.DataFrame
print(result.predictions)
print(result.model, result.request_id)
```

[`Client.forecast`][fomo.client.client.Client.forecast] restores the native type of `past`. Polars in → polars out. A column dict in → a column dict out. A `{columns, data}` dict in → the same row-matrix shape out.

JSON curl uses `{columns, data}` or a column dict instead; see [Quickstart](../getting-started/quickstart.md). Field meanings live on [`ForecastRequest`][fomo.types.models.ForecastRequest] ([API reference](../reference/api.md#fomo.types.models.ForecastRequest)).

## Infer `time` and `target`

If you omit `time`, [`coerce_request`][fomo.types.converters.coerce_request] uses the first column of `past`. If you omit `target`, every `past` column other than `time` and the columns of `future` (if present) is inferred.

```python
result = client.forecast(past=past, fh=3, model="naive")
```

A string `target` is wrapped as a one-element list at coerce time.

## Timeouts and a custom transport

[`Client`][fomo.client.client.Client] passes `url` and `timeout` (default `60.0`) to [`HttpTransport`][fomo.client.transports.http.HttpTransport] when `transport` is omitted. Inject a prebuilt transport to reuse an `httpx.Client` or to swap the wire:

```python
import httpx
from fomo.client import Client
from fomo.client.transports.http import HttpTransport

httpx_client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=120.0)
transport = HttpTransport("http://127.0.0.1:8000", httpx_client=httpx_client)

with Client("http://127.0.0.1:8000", transport=transport) as client:
    result = client.forecast(past=past, fh=3, model="naive")
```

When `transport` is given, `url` and `timeout` are ignored. Implement [`BaseTransport`][fomo.client.transports.base.BaseTransport] for a non-HTTP lane; [`Client`][fomo.client.client.Client] still runs the wire converters and only hands metadata plus named Arrow blobs to `forecast`.
