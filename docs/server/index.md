# Server

The server is the process you start. It loads models, keeps them warm, and answers predict requests. The dashboard, OpenAPI, and `/predict` are that process.

A bare `tserve` loads `naive` only. Name models to load them too. `GET /models` lists what loaded, not the [catalog](../models/index.md). Which extra or image each model needs: [Dependencies](../models/index.md#dependencies).

## Start

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
    ```

    Token, cache, GPU, other tags: [Docker](docker.md).

=== "uv"

    ```bash
    uv pip install "tserve[server,hub]"
    uv run tserve chronos_bolt ttm_r3
    ```

=== "pip"

    ```bash
    pip install "tserve[server,hub]"
    tserve chronos_bolt ttm_r3
    ```

    This installs CUDA torch (MPS on macOS). A CPU wheel: [CPU-only install](pip.md#cpu-only-install).

Another family is the same command with that row's tag and model. `moirai_2`:

```bash
docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
```

Startup prints:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

```bash
curl -s http://127.0.0.1:8000/models
```

`GET /health` is liveness. Then [predict](../client/http.md).

CLI flags and [`Server`][tserve.server.serve.Server]: [UV / Pip](pip.md). A clone: [From source](source.md). Each family's command: [catalog](../models/index.md#start).

## In this section

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } **Docker**

    ---

    Pull a tag, mount the Hub cache, pass a token, or build the image yourself.

    [:octicons-arrow-right-24: Docker](docker.md)

-   :material-language-python:{ .lg .middle } **UV / Pip**

    ---

    Install from PyPI, then `tserve` or [`Server`][tserve.server.serve.Server].

    [:octicons-arrow-right-24: UV / Pip](pip.md)

-   :material-console:{ .lg .middle } **From source**

    ---

    Install from a clone, then `tserve` or [`Server`][tserve.server.serve.Server].

    [:octicons-arrow-right-24: From source](source.md)

-   :material-code-braces:{ .lg .middle } **Live objects**

    ---

    Serve an estimator you configured in Python. CLI cannot do this.

    [:octicons-arrow-right-24: Live objects](live-objects.md)

-   :material-text:{ .lg .middle } **Craft specs**

    ---

    Load a sktime craft spec as `(id, spec)` or CLI `id=spec`.

    [:octicons-arrow-right-24: Craft specs](craft-specs.md)

-   :material-folder-zip-outline:{ .lg .middle } **Models from a directory**

    ---

    Load sktime `.zip` files by stem. Mix them with registry models.

    [:octicons-arrow-right-24: Models from a directory](models-dir.md)

-   :material-cube-outline:{ .lg .middle } **Which models to load**

    ---

    One page per extra and image tag, with the models each one can serve.

    [:octicons-arrow-right-24: Catalog](../models/index.md)

-   :material-monitor-dashboard:{ .lg .middle } **Dashboard**

    ---

    Browser console at `GET /`. It talks to the JSON endpoints of this process.

    [:octicons-arrow-right-24: Dashboard](dashboard.md)

</div>
