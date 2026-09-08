# Server

The server is the process you start. It loads the models you name, keeps them warm, and answers forecast requests. Dashboard, OpenAPI, and `/forecast` all belong to that process.

Nothing loads unless you name it. A bare `fomo serve` starts empty. `GET /models` lists what this process loaded, not the [catalog](../models/index.md). Which ids exist, and which extra or image tag each one needs, is on [Dependencies](../models/index.md#dependencies).

## Quick start

**Docker**

The `hub` image can load both models used throughout the client guides. Arguments replace the image `CMD`, which otherwise loads `naive`.

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt timesfm-2.5
```

Token, cache volume, GPU, and tags: [Docker](docker.md).

**From source**

Python >= 3.12. Clone over HTTPS. FoMo is not on PyPI yet. The extras here match the `hub` image; swap them when you load other families.

=== "uv"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    uv sync --extra server --extra hub
    uv run fomo serve --load-models chronos-bolt timesfm-2.5
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/fomo.git && cd fomo
    pip install -e ".[server,hub]"
    fomo serve --load-models chronos-bolt timesfm-2.5
    ```

CLI flags, `Server`, and `server.app`: [From source](source.md).

**Load a different family**

The commands above load `hub` ids. Every other family follows the same three steps: find the id in the [catalog](../models/index.md), read the extra and image tag listed with its family, then install that extra and name the id in `--load-models`. `moirai-2` sits in the `moirai` extra:

=== "uv"

    ```bash
    uv sync --extra server --extra moirai
    uv run fomo serve --load-models moirai-2
    ```

=== "pip"

    ```bash
    pip install -e ".[server,moirai]"
    fomo serve --load-models moirai-2
    ```

In Docker the tag plays the role of the extra — `geetu040/fomo:moirai` for that same id, as in [Choose which models to load](docker.md#choose-which-models-to-load).

Once the process is up, the terminal prints the URLs:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Confirm what loaded:

```bash
curl -s http://127.0.0.1:8000/models
```

`GET /health` is liveness, not “models are warm”. Then [forecast](../client/http.md).

## In this section

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } **Docker**

    ---

    Pull a tag, mount the Hub cache, pass a token, or build the image yourself.

    [:octicons-arrow-right-24: Docker](docker.md)

-   :material-console:{ .lg .middle } **From source**

    ---

    Install from a clone, then `fomo serve` or [`Server`][fomo.server.serve.Server].

    [:octicons-arrow-right-24: From source](source.md)

-   :material-code-braces:{ .lg .middle } **Live objects**

    ---

    Serve an estimator you configured in Python. CLI cannot do this.

    [:octicons-arrow-right-24: Live objects](live-objects.md)

-   :material-folder-zip-outline:{ .lg .middle } **Models from a directory**

    ---

    Load sktime `.zip` files by stem. Mix them with registry ids.

    [:octicons-arrow-right-24: Models from a directory](models-dir.md)

-   :material-monitor-dashboard:{ .lg .middle } **Dashboard**

    ---

    Browser console at `GET /`. It talks to the JSON endpoints of this process.

    [:octicons-arrow-right-24: Dashboard](dashboard.md)

</div>
