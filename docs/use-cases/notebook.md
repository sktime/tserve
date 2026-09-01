# Notebook and a local server

Keep a `fomo serve` process running in a terminal. From a notebook, talk to it with [`Client`][fomo.client.client.Client].

Terminal:

```bash
uv pip install -e '.[server,sktime-lite,client]'
fomo serve --load-models naive
```

Notebook:

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
        model="naive",
    )

result.predictions
```

Point [`Client`][fomo.client.client.Client] at the host and port you actually used (`Client("http://127.0.0.1:8000")` matches the CLI defaults). Do not start a second [`Server()`][fomo.server.serve.Server] in the notebook unless you pick another port; [`Server.run`][fomo.server.serve.Server.run] blocks on uvicorn.

For in-process embedding instead of a separate CLI process, see [Embed Server](embed-server.md).
