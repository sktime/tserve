# Client

JSON goes to `POST /predict`. The Python [`Client`][tserve.client.client.Client] posts Arrow to `POST /predict/bytes`. Same fields either way. The URL is a server you started.

## Start a server

Point forecasts below use `chronos_bolt`. Quantile examples on the next pages use `timesfm_2_5`:

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt timesfm_2_5
```

Other tags and installers: [Server](../server/index.md). `GET /models` lists what this process loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

## Predict

Five days of sales, next three steps, `chronos_bolt`:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "chronos_bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"past":{"timestamp":["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],"sales":[120,135,128,142,138]},"time":"timestamp","target":["sales"],"fh":3,"model":"chronos_bolt"}'
    ```

The response is `predictions`, `quantiles`, `model`, and `request_id`. Fields and formats: [Data specification](data.md).

## In this section

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } **HTTP**

    ---

    Send JSON to `POST /predict` from any language. Covers every route.

    [:octicons-arrow-right-24: HTTP](http.md)

-   :material-language-python:{ .lg .middle } **Python**

    ---

    Pass native tables to [`Client`][tserve.client.client.Client]. It posts Arrow.

    [:octicons-arrow-right-24: Python](python.md)

-   :material-table-column:{ .lg .middle } **Data specification**

    ---

    Request fields, table formats, column inference, and response shape.

    [:octicons-arrow-right-24: Data specification](data.md)

</div>
