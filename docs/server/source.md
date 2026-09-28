# From source

Python >= 3.12, and a clone over HTTPS. [uv](https://docs.astral.sh/uv/) is the shorter path, pip works everywhere. For the published package, see [UV / Pip](pip.md).

## Install

=== "uv"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    uv sync --extra server --extra hub
    ```

=== "pip"

    ```bash
    git clone https://github.com/sktime/tserve.git && cd tserve
    pip install -e ".[server,hub]"
    ```

`server` is enough to serve `naive` (a test baseline). The `hub` extra above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Do not add `client` on a machine that only serves.

## Dependencies

--8<-- "includes/model-dependencies.md"

Replace `hub` in the install above with another extra from the table. uv repeats `--extra` (`uv sync --extra server --extra chronos`). pip takes one list (`".[server,chronos]"`). `full` is the union extra. `all-extras` is a pip convenience for `client,server,full` and is not a Docker tag. Each extra's command and models: [catalog](../models/index.md#start-a-server).

A CPU build of torch: [CPU-only install](pip.md#cpu-only-install).

--8<-- "includes/serve.md"

## Next

- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
