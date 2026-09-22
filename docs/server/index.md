# Server

The server is the process you start. It loads models, keeps them warm, and answers predict requests. Dashboard, OpenAPI, and `/predict` all belong to that process.

Nothing extra loads unless you name it. A bare `tserve` still loads `naive`, enough to test the process. Name a catalog model for a real forecast. `GET /models` lists what this process loaded, not the [catalog](../models/index.md). Which models exist, and which extra or image tag each one needs, is on [Dependencies](../models/index.md#dependencies).

## Quick start

**Docker**

The `hub` image can load both models used throughout the client guides. Extra models after the image name load alongside `naive`.

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
```

Token, cache volume, GPU, and tags: [Docker](docker.md).

**UV / Pip**

Python >= 3.12. The extras here match the `hub` image; swap them when you load other families.

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

    The `gpu` extra does not work with pip. This install already pulls CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](pip.md#gpu).

CLI flags, `Server`, and `server.app`: [UV / Pip](pip.md). Editable installs from a clone: [From source](source.md).

**Load a different family**

The commands above load [`hub`](../models/hub.md) models. Every other family follows the same three steps: find the model in the [catalog](../models/index.md#all-models), read the extra and image tag listed with its family, then install that extra and name the model as a leftover positional. `moirai_2` sits in the [`moirai`](../models/moirai.md) extra:

=== "Docker"

    ```bash
    docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
    ```

=== "uv"

    ```bash
    uv pip install "tserve[server,moirai]"
    uv run tserve moirai_2
    ```

=== "pip"

    ```bash
    pip install "tserve[server,moirai]"
    tserve moirai_2
    ```

The Docker tag plays the role of the extra — `sktime/tserve:moirai` for that same model, as in [Choose which models to load](docker.md#choose-which-models-to-load). Each extra has its own catalog page with both forms of that command and the models it can load: [base](../models/base.md), [hub](../models/hub.md), [chronos](../models/chronos.md), [kronos](../models/kronos.md), [granite](../models/granite.md), [moirai](../models/moirai.md), [tirex](../models/tirex.md), [toto](../models/toto.md), [mantis](../models/mantis.md), [full](../models/full.md).

Once the process is up, the terminal prints the URLs:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Confirm what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

`GET /health` is liveness, not “models are warm”. Then [predict](../client/http.md).

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
