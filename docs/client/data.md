# Data specification

HTTP and the Python client share one forecast contract. Only the transport
changes: JSON embeds tables in the request, while the Python client converts
them to Arrow.

## Request fields

| field | required | description |
| --- | --- | --- |
| `past` | yes | Historical observations as a table. It must contain the time column and every target column. |
| `fh` | yes | Number of steps ahead. Must be greater than zero. |
| `time` | no | Name of the time column. Defaults to the first column of `past`. |
| `target` | no | Target column name or list of names. See [column inference](#column-inference). |
| `model` | no | Loaded model id. Defaults to `naive`, which must still be loaded. |
| `future` | no | Future table. When present, it must contain the time column. |
| `static` | no | One row of values that remain constant over time. |
| `quantiles` | no | Quantile levels passed to models that support quantile forecasts. |

`past` is not a 1-d vector or a pandas index. It is a table with one row per
timestamp:

```json
{
  "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
  "sales": [120, 135, 128]
}
```

Time must be a column. For a pandas object with time in its index, use
`reset_index()` before sending it.

## Table formats

### Column-oriented dictionaries

Each key is a column name. Each value is a list, and all lists must have the
same length:

```json
{
  "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
  "sales": [120, 135, 128]
}
```

This format works in JSON and Python.

### Row-oriented dictionaries

Use `columns` plus a list of rows. Each row must have one value for every
column:

```json
{
  "columns": ["timestamp", "sales"],
  "data": [
    ["2024-01-01", 120],
    ["2024-01-02", 135],
    ["2024-01-03", 128]
  ]
}
```

The dictionary must contain only `columns` and `data`. This format also works
in JSON and Python.

### Python tables

[`Client.forecast(...)`][fomo.client.client.Client.forecast] also accepts
pandas, polars, pyarrow, and Narwhals tables:

=== "pandas"

    ```python
    import pandas as pd

    past = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="D"),
            "sales": [120, 135, 128],
        }
    )
    ```

=== "polars"

    ```python
    import polars as pl

    past = pl.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "sales": [120, 135, 128],
        }
    )
    ```

=== "pyarrow"

    ```python
    import pyarrow as pa

    past = pa.table(
        {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "sales": [120, 135, 128],
        }
    )
    ```

=== "Narwhals"

    ```python
    import narwhals as nw
    import pandas as pd

    past = nw.from_native(
        pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="D"),
                "sales": [120, 135, 128],
            }
        ),
        eager_only=True,
    )
    ```

These native frames are Python inputs. JSON `POST /forecast` uses one of the
two dictionary shapes above.

## Column roles

### Time

`time` identifies the time column:

```json
{
  "time": "timestamp"
}
```

If `time` is omitted, FoMo uses the first column of `past`. The same column
must also exist in `future` when a future table is supplied.

The sktime executor preserves valid integer and datetime indexes. String time
values, such as dates in JSON, are parsed as datetimes.

### Targets

`target` accepts one name or a list:

```json
{
  "target": ["sales", "returns"]
}
```

A single string is normalized to a one-element list. Multiple targets work
only when the loaded estimator supports multivariate forecasting.

### Column inference

You may omit `time` and `target`:

```json
{
  "past": {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "sales": [120, 135, 128]
  },
  "fh": 3,
  "model": "chronos-bolt-tiny"
}
```

FoMo then uses:

1. the first `past` column as `time`;
2. every other `past` column as a target, except columns also present in
   `future`.

Specify `target` explicitly when a table contains columns that should not be
forecast.

## Forecast horizon and model

`fh` is a relative horizon. `fh: 3` requests the next three steps after the
last row in `past`.

`model` is a registry id loaded by the running process. It is not an executor
name. If omitted, it defaults to `naive`; a server that did not load `naive`
will reject that request. Use `GET /models` to see loaded ids and the
[catalog](../models/catalog.md) to see available ids.

## Future and static data

`static` represents values that do not change over time. Supply one row:

```json
{
  "static": {
    "store_type": ["urban"],
    "region": ["EU-west"]
  }
}
```

The current sktime executor takes the first `static` row and broadcasts it
across the historical and forecast horizons.

`future` can supply the forecast timestamps:

```json
{
  "future": {
    "timestamp": ["2024-01-06", "2024-01-07", "2024-01-08"]
  }
}
```

When `future` is omitted, the executor derives the next `fh` index values.

Extra values in `past` and `future` are accepted by the transport, but the
current sktime conversion does not pass them to the estimator as
time-varying covariates. Other `future` columns only affect automatic target
inference. Static values are the supported exogenous input today.

## Quantiles

Request quantile levels with a list:

```json
{
  "quantiles": [0.1, 0.5, 0.9]
}
```

The loaded estimator must implement quantile prediction. `timesfm-2.5`
supports the levels above; Chronos Bolt does not. FoMo forwards the values to
the estimator, which may apply additional validation.

Point forecasts remain in `predictions`. Quantile forecasts are returned as a
second table whose columns use `{target}_{level}`, for example `sales_0.1`,
`sales_0.5`, and `sales_0.9`.

## Response

Every successful forecast returns:

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00"],
    "sales": [139.96]
  },
  "quantiles": null,
  "model": "chronos-bolt-tiny",
  "request_id": "…"
}
```

- `predictions` contains the time column and point forecasts.
- `quantiles` is a second table when requested and supported; otherwise it is
  `null` over JSON and `None` in Python.
- `model` is the id that served the request.
- `request_id` identifies this call and is also included in forecast error
  responses.

JSON responses always use column-oriented dictionaries. The Python client
restores `predictions` and `quantiles` to the type used for `past`: a column
dict, row dict, pandas DataFrame, polars DataFrame, pyarrow Table, or Narwhals
DataFrame.

## Validation and limits

FoMo rejects requests when:

- `past` or `fh` is missing;
- `fh` is not greater than zero;
- dictionary columns have different lengths;
- a row has a different width from `columns`;
- `past` does not contain the selected time and target columns;
- `future` is present without the selected time column;
- target inference leaves no target columns.

Panel and hierarchical inputs are not supported. Send one time series table
per request. See [Errors](../reference/errors.md) for HTTP statuses and Python
exceptions.
