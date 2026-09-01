# Quantile forecasts

When `quantiles` is a non-empty list, [`SktimeExecutor.predict`][fomo.runtime.executors.sktime.executor.SktimeExecutor.predict] also calls the estimator's `predict_quantiles`. Estimators that cannot return quantiles fail that call (HTTP 400 on JSON; `RuntimeError` from [`Client`][fomo.client.client.Client]).

FoMo has no capability flag. Whether an id works is the estimator's. `naive` supports quantiles with no Hub download. Foundation-model examples below use `flowstate` (or swap `timesfm-2.5-200m`).

[`to_response`][fomo.runtime.executors.sktime.converters.to_response] flattens quantile columns to `{variable}_{alpha}` (sktime variable names; often positional `0`, for example `0_0.1`). Values are model output; they are not sorted or clipped.

## Local `naive`

```bash
fomo serve --load-models naive
```

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
    result = client.forecast(
        past=past,
        time="timestamp",
        target=["sales"],
        fh=3,
        quantiles=[0.1, 0.5, 0.9],
        model="naive",
    )

print(result.predictions)
print(result.quantiles)
```

`predictions` remains the point forecast. `quantiles` is a second table, or `None` when the field was omitted.

JSON:

```bash
curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "past": {
      "timestamp": ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],
      "sales": [120, 135, 128, 142, 138]
    },
    "time": "timestamp",
    "target": ["sales"],
    "fh": 3,
    "quantiles": [0.1, 0.5, 0.9],
    "model": "naive"
  }'
```

## Hub model (`flowstate` or `timesfm-2.5-200m`)

Needs the `sktime` extra. First load downloads weights from Hugging Face:

```bash
uv pip install -e '.[server,sktime]'
fomo serve --load-models flowstate
```

Use the same [`Client.forecast`][fomo.client.client.Client.forecast] call with `model="flowstate"` (or `"timesfm-2.5-200m"` on a server that loaded that id). See [Extras and Hub weights](../how-to/extras.md).
