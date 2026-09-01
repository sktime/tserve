# Covariates

A forecast request is tables plus column-role names. [`ForecastRequest`][fomo.types.models.ForecastRequest] accepts optional `future` and `static` frames. [`coerce_request`][fomo.types.converters.coerce_request] converts them to narwhals; if `future` is set, [`CoercedForecastRequest`][fomo.types.models.CoercedForecastRequest] requires the `time` column on that table.

The sktime domain mapping is [`from_request`][fomo.runtime.executors.sktime.converters.from_request]:

- Target `y` is the `target` columns of `past`, indexed by `time`.
- If `static` is omitted, both `X` and `X_future` are `None`. Dynamic columns on `future` are not used in that case.
- If `static` is set, the **first row** is broadcast as constant exogenous columns over the past index (`X`) and over the future index (`X_future`). The future index comes from `future` when that table is present; otherwise it is `fh` steps after the last past timestamp.

There is no `known_future` or `series_id` field on the current schema. Panel (multi-series) input is not supported: [`from_request`][fomo.runtime.executors.sktime.converters.from_request] maps a single series from `past`, `time`, and `target`.

## Static features

```python
import pandas as pd
from fomo.client import Client

past = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
        "sales": [120, 135, 128, 142, 138],
    }
)
static = pd.DataFrame({"store_type": ["urban"]})
future = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-06", periods=3, freq="D"),
    }
)

with Client("http://127.0.0.1:8000") as client:
    result = client.forecast(
        past=past,
        future=future,
        static=static,
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
    )

print(result.predictions)
```

`static` is not a time series. Extra columns on `past` that are not `time` or `target` stay in the past frame but are not mapped onto sktime `X` unless they also appear as the broadcast static row.

## `future` without `static`

You can still send `future`. After coercion it must include `time`. With the current [`SktimeExecutor`][fomo.runtime.executors.sktime.executor.SktimeExecutor], that table is ignored for `fit` / `predict` unless `static` is also set (in which case only its **index** is used).

JSON curl uses `{columns, data}` or a column dict for `past` / `future` / `static`; see the [HTTP](../reference/http.md) page. Roles are explained in [Forecast tables](../concepts/forecast-tables.md).
