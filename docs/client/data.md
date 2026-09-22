# Data specification

HTTP and the Python client share one predict contract. Only the transport changes: JSON embeds tables in the request, while the Python client converts them to Arrow.

## Request fields

| field | required | description |
| --- | --- | --- |
| `past` | yes | Historical observations as a table. It must contain the time column and every target column. |
| `fh` | yes | Number of steps ahead. Must be greater than zero. |
| `time` | no | Name of the time column. Defaults to the first column of `past`. |
| `target` | no | Target column name or list of names. See [column inference](#column-inference). |
| `model` | no | Loaded model. Defaults to `naive`. |
| `future` | no | Future values of time-varying covariates. When present, it must contain the time column. |
| `static` | no | One row of values that remain constant over time. |
| `quantiles` | no | Quantile levels passed to models that support quantile forecasts. |

`past` is not a 1-d vector or a pandas index. It is a table with one row per timestamp:

```json
{
  "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
  "sales": [120, 135, 128]
}
```

Time must be a column. For a pandas object with time in its index, use `reset_index()` before sending it.

## Table formats

### Column-oriented dictionaries

Each key is a column name. Each value is a list, and all lists must have the same length:

```json
{
  "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
  "sales": [120, 135, 128]
}
```

JSON and Python both accept this shape.

### Row-oriented dictionaries

Use `columns` plus a list of rows. Each row must have one value for every column:

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

The dictionary must contain only `columns` and `data`. JSON and Python both accept this shape.

### Python tables

[`Client.predict(...)`][tserve.client.client.Client.predict] also accepts pandas, polars, pyarrow, and Narwhals tables:

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

These native frames are Python inputs. JSON `POST /predict` uses one of the two dictionary shapes above.

## Column roles

### Time

`time` names the time column. Omitted, it is the first column of `past`. When you send `future`, that column has to be there too.

Integer and datetime values are kept. Strings, including JSON dates, are parsed as datetimes.

### Targets

`target` is one name or a list. A string becomes a one-element list. More than one target needs an estimator that supports multivariate forecasting. Which families do: [Capabilities](../models/index.md#capabilities).

### Column inference

You may omit `time` and `target`:

```json
{
  "past": {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "sales": [120, 135, 128]
  },
  "fh": 3,
  "model": "chronos_bolt"
}
```

TServe then uses:

1. the first `past` column as `time`;
2. every other `past` column as a target, except columns also present in `future`, which become exogenous features instead.

Specify `target` explicitly when a table contains columns that should not be forecast.

## Prediction horizon and model

`fh` is a relative horizon. `fh: 3` requests the next three steps after the last row in `past`.

`model` is a registry model loaded by the running process. It is not an executor name. If omitted, it defaults to `naive`. Use `GET /models` to see loaded models and the [catalog](../models/index.md) to see available models.

## Future and static data

`static` is one row of values that do not change. The sktime executor broadcasts that row across history and the forecast.

`future` is values you already know for the steps being forecast, such as a planned promotion. A non-target column is passed through only when it is in **both** `past` and `future`. A `past`-only column has no future values; a `future`-only column has no history. Estimators tagged `capability:exogenous` use the column; others ignore it.

`fh` stays relative: the forecast is the next `fh` steps after the last `past` row. `future` must hold a row for each of those steps. Extra rows are ignored. A `future` that skips the horizon is rejected. Omit `future` and the executor builds that index, so `static` alone needs no `future` table.

```json
{
  "past": {
    "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    "sales": [120, 135, 128, 142, 138],
    "promo": [0, 1, 0, 0, 1]
  },
  "future": {
    "timestamp": ["2024-01-06", "2024-01-07", "2024-01-08"],
    "promo": [1, 0, 0]
  },
  "static": {"store_type": ["urban"]},
  "time": "timestamp",
  "target": ["sales"],
  "fh": 3,
  "model": "chronos_2"
}
```

## Quantiles

Request quantile levels with a list:

```json
{
  "model": "timesfm_2_5",
  "quantiles": [0.1, 0.5, 0.9]
}
```

The loaded estimator must support quantile prediction. `timesfm_2_5` supports the levels above; Chronos Bolt and TTM do not. TServe forwards the values to the estimator, which may apply additional validation.

Point forecasts remain in `predictions`. Quantile forecasts are returned as a second table. Many estimators name those columns `{target}_{level}` (`sales_0.1`, `sales_0.5`, `sales_0.9`); `timesfm_2_5` currently uses a positional prefix (`0_0.1`, `0_0.5`, `0_0.9`).

## Response

Every successful prediction returns:

```json
{
  "predictions": {
    "timestamp": ["2024-01-06T00:00:00"],
    "sales": [139.96]
  },
  "quantiles": null,
  "model": "chronos_bolt",
  "request_id": "…"
}
```

- `predictions` contains the time column and point forecasts.
- `quantiles` is a second table when requested and supported; otherwise it is `null` over JSON and `None` in Python.
- `model` is the model that served the request.
- `request_id` identifies this call and is also included in predict error responses.

JSON responses always use column-oriented dictionaries. The Python client restores `predictions` and `quantiles` to the type used for `past`: a column dict, row dict, pandas DataFrame, polars DataFrame, pyarrow Table, or Narwhals DataFrame.

## Validation and limits

TServe rejects requests when:

- `past` or `fh` is missing;
- `fh` is not greater than zero;
- dictionary columns have different lengths;
- a row has a different width from `columns`;
- `past` does not contain the selected time and target columns;
- `future` is present without the selected time column;
- target inference leaves no target columns.

Panel and hierarchical inputs are not supported. Send one time series table per request. See [Errors](../reference/errors.md) for HTTP statuses and Python exceptions.
