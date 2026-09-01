# Docker sidecar and curl

Run FoMo as a local container and call JSON `POST /forecast` from the host. The repo image `CMD` loads `naive`; extra `docker run` args replace that `CMD`. The `ENTRYPOINT` already binds `0.0.0.0:8000`.

```bash
docker build -t fomo:local .
docker run --rm -p 8000:8000 fomo:local
```

From another terminal:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/models

curl -s http://127.0.0.1:8000/forecast \
  -H 'Content-Type: application/json' \
  -d '{
    "past": {
      "columns": ["timestamp", "sales"],
      "data": [
        ["2024-01-01", 120],
        ["2024-01-02", 135],
        ["2024-01-03", 128],
        ["2024-01-04", 142],
        ["2024-01-05", 138]
      ]
    },
    "time": "timestamp",
    "target": ["sales"],
    "fh": 3,
    "model": "naive"
  }'
```

Publish with `-p 8000:8000` (or another host port mapped to container `8000`). Live Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Hub models need the `sktime` extra at **build** time:

```bash
docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
docker run --rm -p 8000:8000 fomo:sktime --load-models naive flowstate
```

See [Installation](../getting-started/installation.md) and [Run the server](../how-to/run-server.md).
