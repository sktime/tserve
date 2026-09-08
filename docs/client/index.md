# Client

Send predictions to a FoMo server over HTTP or from Python. Both paths use the
same request fields and return the same prediction content:

- [HTTP](http.md) sends JSON to `POST /predict` from any language.
- [Python](python.md) accepts native tables and sends Arrow to
  `POST /predict/bytes`.

FoMo is not a hosted API. The URL points to a server process you started.

## Start a server

For the examples in this section, start the `hub` image with
`chronos-bolt` and `timesfm-2.5` loaded:

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt timesfm-2.5
```

The first start downloads model weights. See [Server](../server/index.md)
for source installs and server options, or [Docker](../server/docker.md) for image
tags, GPU support, Hugging Face tokens, and cache volumes.

Check which ids this process loaded:

=== "bash / zsh"

    ```bash
    curl -s http://127.0.0.1:8000/models
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/models
    ```

`GET /models` lists loaded ids, not every id in the
[catalog](../models/index.md).

## Data at a glance

A predict request combines a table with the roles of its columns:

- `past` is the historical table. Time must be a column, alongside one or more
  target columns.
- `time` names the time column and `target` names the columns to forecast.
- `fh` is the number of steps ahead.
- `model` is an id loaded by this server.

The HTTP endpoint accepts column-oriented and row-oriented JSON. The Python
client also accepts pandas, polars, pyarrow, and Narwhals tables. See
[Data specification](data.md) for every field, format, default, and limitation.

## First prediction

This request sends five days of sales and asks `chronos-bolt` for the next
three days:

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
      "model": "chronos-bolt"
    }'
    ```

=== "PowerShell"

    ```powershell
    curl.exe -s http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{
      "past": {
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "sales": [120, 135, 128, 142, 138]
      },
      "time": "timestamp",
      "target": ["sales"],
      "fh": 3,
      "model": "chronos-bolt"
    }'
    ```

The response contains a `predictions` table, the model id, a request id, and
optional quantiles. Continue with [HTTP](http.md) for JSON examples or
[Python](python.md) for native Python tables.

## In this section

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } **HTTP**

    ---

    Send JSON to `POST /predict` from any language. Covers every route.

    [:octicons-arrow-right-24: HTTP](http.md)

-   :material-language-python:{ .lg .middle } **Python**

    ---

    Pass native tables to [`Client`][fomo.client.client.Client]. It posts Arrow.

    [:octicons-arrow-right-24: Python](python.md)

-   :material-table-column:{ .lg .middle } **Data specification**

    ---

    Request fields, table formats, column inference, and response shape.

    [:octicons-arrow-right-24: Data specification](data.md)

</div>
