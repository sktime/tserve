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
    "data": {
      "columns": ["timestamp", "sales"],
      "data": [
        ["2024-01-01", 120],
        ["2024-01-02", 135],
        ["2024-01-03", 128],
        ["2024-01-04", 142],
        ["2024-01-05", 138]
      ]
    },
    "target_columns": ["sales"],
    "time_column": "timestamp",
    "horizon": 3,
    "freq": "D",
    "model": "dummy"
  }'
```

Example response:

```json
{
  "predictions": {
    "columns": ["sales"],
    "data": [[138.0], [138.0], [138.0]]
  },
  "quantiles": null,
  "model": "dummy",
  "request_id": "..."
}
```

## Request fields


| Field          | Role                                                             |
| -------------- | ---------------------------------------------------------------- |
| `data`         | Target history (and optional inline past exog)                   |
| `exog_data`    | Full exog timeline when future covariates are known              |
| `horizon`      | Steps to forecast (alias: `fh`)                                  |
| `freq`         | Series frequency (`D`, `H`, `5min`, ...) for models that need it |
| `context`      | Max history rows to use (most recent)                            |
| `quantiles`    | Probabilistic output, e.g. `[0.1, 0.5, 0.9]`                     |
| `model_config` | Model-specific overrides, e.g. `{"freq": "D"}`                   |


See `GET /models` for model capabilities and `GET /health` for loaded models.