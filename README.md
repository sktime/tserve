# FoMo

Time series foundation model inference server (early prototype).

## Setup

```bash
uv sync
uv run uvicorn fomo.app:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

By default only `dummy` is preloaded. Override with `FOMO_PRELOAD_MODELS`, e.g.
```bash
FOMO_PRELOAD_MODELS=dummy,chronos2 uv run uvicorn fomo.app:app --reload
```

## End-to-end example

Five daily sales observations, forecast three steps ahead with the `dummy` model
(NaiveForecaster, no download required):

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "time": "timestamp",
    "target": ["sales"],
    "history": {
      "columns": ["timestamp", "sales"],
      "data": [
        ["2024-01-01", 120],
        ["2024-01-02", 135],
        ["2024-01-03", 128],
        ["2024-01-04", 142],
        ["2024-01-05", 138]
      ]
    },
    "horizon": 3,
    "freq": "D",
    "model": "dummy"
  }'
```

Example response:

```json
{
  "predictions": {
    "columns": ["timestamp", "sales"],
    "data": [
      ["2024-01-06T00:00:00", 138.0],
      ["2024-01-07T00:00:00", 138.0],
      ["2024-01-08T00:00:00", 138.0]
    ]
  },
  "quantiles": null,
  "model": "dummy",
  "request_id": "..."
}
```

## Request fields

Long tables plus explicit roles. Unlisted columns are ignored. Omit empty role lists.

| Field | Required | Role |
| --- | --- | --- |
| `history` | yes | Long table: one row per series x observed timestamp |
| `future` | if `known_future` is set | Horizon covariates only. No targets. Exactly `horizon` timestamps per series |
| `static` | if static features exist | One row per series |
| `series_id` | no | Key columns, MultiIndex order. Omit for a single series |
| `time` | yes | Timestamp column |
| `target` | yes | Target names. Always a list |
| `known_future` | no | Dynamic covariates in both `history` and `future` |
| `past_only` | no | Dynamic covariates on `history` only (kept for later backends; not sktime `X`) |
| `horizon` | yes | Steps to forecast (alias: `fh`) |
| `freq` | no | Pandas offset (`D`, `MS`, `H`, ...). Not inferred |
| `quantiles` | no | Probabilistic output, e.g. `[0.1, 0.5, 0.9]` |
| `model_config` | no | Model-specific overrides |
| `model` | yes | Loaded estimator alias |

`{columns, data}` is the table encoding. The same roles apply later to pandas frames or numpy arrays sent as raw bytes.

See `GET /models` for model capabilities and `GET /health` for loaded models.