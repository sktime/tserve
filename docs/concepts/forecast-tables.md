# Forecast tables

A forecast request is one or more tables plus column-role names. The user-facing schema is [`ForecastRequest`][fomo.types.models.ForecastRequest] in and [`ForecastResponse`][fomo.types.models.ForecastResponse] out. Construction checks table **shape** only. Column names are enforced after [`coerce_request`][fomo.types.converters.coerce_request] on [`CoercedForecastRequest`][fomo.types.models.CoercedForecastRequest].

`model` is a **loaded model id** (registry id, zip stem, or the id passed with an in-process forecaster), not an executor name such as `"sktime"`. Default is `"naive"`.

## Request fields

| field | required | |
| --- | --- | --- |
| `past` | yes | past observations |
| `fh` | yes | forecast steps (`> 0`) |
| `time` | no | timestamp column in `past` / `future` / predictions; omitted → first column of `past` |
| `target` | no | target column name or list; a string is wrapped as a one-element list; omitted → every `past` column other than `time` and `future` columns |
| `model` | no (default `"naive"`) | loaded estimator id |
| `future` | no | future rows; if set, must include `time` after coercion |
| `static` | no | static features; sktime broadcasts the first row over time |
| `quantiles` | no | quantile alphas; forwarded to `predict_quantiles` when set |

There is no `history`, `horizon`, `context`, `freq`, `params`, `series_id`, or `known_future` field on the current models.

## Roles

| role | what it is |
| --- | --- |
| **past** | Past observations. After coercion must include `time` and every `target`. |
| **future** | Optional future rows. If present, must contain `time`. With the current sktime converter, this table supplies the future **index** when `static` is set; see [Covariates](../tutorials/covariates.md). |
| **static** | Optional per-series (or single-row) features. Not a time series. First row is broadcast as exogenous `X` / `X_future`. |

## Accepted frame shapes

`past`, `future`, `static`, `predictions`, and `quantiles` may be:

- a pandas-like DataFrame
- a polars DataFrame
- a pyarrow Table
- a narwhals DataFrame
- a column-oriented dict (name → list of equal length)
- a row matrix `{"columns": [...], "data": [[...], ...]}`

`None` is allowed for optional frames. JSON tables are typically `{columns, data}` or a column dict. Extra keys besides `columns` and `data` on a row-matrix dict are rejected.

After coercion, `past` must contain `time` and every `target`. Empty inferred `target` lists fail on [`CoercedForecastRequest`][fomo.types.models.CoercedForecastRequest], not on [`ForecastRequest`][fomo.types.models.ForecastRequest].

JSON `POST /forecast` returns predictions as a column dict. [`Client.forecast`][fomo.client.client.Client.forecast] restores the native type of `past`.

## Two conversion layers

| layer | module | job |
| --- | --- | --- |
| Wire converters | [`fomo.types.converters`][fomo.types.converters] | native frames ↔ narwhals ↔ Arrow IPC ↔ `FOMO` envelope |
| sktime converters | [`fomo.runtime.executors.sktime.converters`][fomo.runtime.executors.sktime.converters] | coerced request ↔ `y`, `X`, `X_future`, `fh` |

Executors and [`Scheduler`][fomo.scheduling.scheduler.Scheduler] only see coerced models. The sktime converter uses the original `time` column as the pandas index; JSON strings are converted with `pandas.to_datetime`.
