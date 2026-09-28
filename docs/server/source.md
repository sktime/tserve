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

Family extras install CUDA torch from PyPI (MPS on macOS). A CPU wheel: [CPU-only install](#cpu-only-install).

## CPU-only install

Family extras pull `torch`, and the installs above take the CUDA wheel from PyPI (MPS on macOS). On a GPU host that is already what you want.

Without a GPU, that wheel is a large download you will never use. Install torch from the CPU index first, then TServe. `uv sync` resolves torch from PyPI, so the CPU order uses `uv pip install` or pip. If a later install replaces that wheel with CUDA, run the torch line again.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[server,hub]"
```

The same order works with `uv pip install`. Swap `hub` for any other family extra from [Dependencies](#dependencies). A GPU host can also use a `*-gpu` image: [GPU images](docker.md#gpu-images).

--8<-- "includes/serve.md"

## Next

- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
