# FoMo

Time series foundation model inference server (early prototype).

## Setup

```bash
uv sync
uv run uvicorn fomo.app:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
