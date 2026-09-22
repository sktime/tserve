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

    The `gpu` extra does not work with pip. Family extras already install CUDA torch from PyPI (MPS on macOS). To force a CPU wheel, install torch separately first — [GPU](#gpu).

`server` is enough to serve `naive` (a test baseline). The `hub` extra above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Do not add `client` on a machine that only serves.

## Dependencies

--8<-- "includes/model-dependencies.md"

Replace `hub` in the install above with another extra from the table. uv repeats `--extra` (`uv sync --extra server --extra chronos`). pip takes one list (`".[server,chronos]"`). `full` is the union extra. `all-extras` is a pip convenience for `client,server,full` and is not a Docker tag. Each extra's command and models: [catalog](../models/index.md#start-a-server).

`gpu` is not a model family. Torch CPU vs GPU: [GPU](#gpu).

## GPU

Family extras pull `torch`. Which wheel you get depends on the installer.

**uv** defaults to the CPU index. Add `--extra gpu` for the PyPI wheel: CUDA on Linux and Windows, MPS on Apple silicon. Pair it with the family extras you need.

```bash
uv sync --extra server --extra hub --extra gpu
```

**pip** does not honor the `gpu` extra. `pip install -e ".[server,hub,gpu]"` is the same as without `gpu`. A normal pip install always takes CUDA torch from PyPI (MPS on macOS).

To **force CPU torch with pip**, install torch from the CPU index first, then TServe. If a later `pip install` replaces that wheel with CUDA, run the torch line again.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[server,hub]"
```

Swap `hub` for any other family extra from [Dependencies](#dependencies). Containers use `*-gpu` tags instead: [Docker](docker.md#gpu-images).

--8<-- "includes/serve.md"

## Next

- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
