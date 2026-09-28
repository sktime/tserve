# UV / Pip

Python >= 3.12. Install TServe from PyPI with [uv](https://docs.astral.sh/uv/) or pip, then start `tserve`. Editable installs from a clone stay on [From source](source.md).

## Install

=== "uv"

    ```bash
    uv pip install "tserve[server,hub]"
    ```

=== "pip"

    ```bash
    pip install "tserve[server,hub]"
    ```

`server` is enough to serve `naive` (a test baseline). The `hub` extra above covers Chronos Bolt/T5, TTM, and TimesFM 2.x. Do not add `client` on a machine that only serves.

## Dependencies

--8<-- "includes/model-dependencies.md"

Replace `hub` in the install above with another extra from the table. `full` is the union extra. `all-extras` is a pip convenience for `client,server,full` and is not a Docker tag. Each extra's command and models: [catalog](../models/index.md#start-a-server).

Family extras install CUDA torch from PyPI (MPS on macOS). A CPU wheel: [CPU-only install](#cpu-only-install).

## CPU-only install

Family extras pull `torch`, and every install here takes the CUDA wheel from PyPI (MPS on macOS). On a GPU host that is already what you want, so nothing below is needed.

Without a GPU, that wheel is a large download you will never use. With pip, install torch from the CPU index first, then TServe. If a later install replaces that wheel with CUDA, run the torch line again.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

```bash
pip install "tserve[server,hub]"
```

uv selects that index in one step with `--torch-backend cpu`:

```bash
uv pip install "tserve[server,hub]" --torch-backend cpu
```

Swap `hub` for any other family extra from [Dependencies](#dependencies). The same commands on a clone: [From source](source.md#cpu-only-install). A GPU host can also use a `*-gpu` image: [GPU images](docker.md#gpu-images).

--8<-- "includes/serve.md"

## Next

- [From source](source.md) — editable install from a clone
- [Live objects](live-objects.md) — Python can also serve estimators you configured in the session
- [Craft specs](craft-specs.md) — load a sktime craft spec as `(id, spec)` or CLI `id=spec`
- [Models from a directory](models-dir.md) — serve saved sktime `.zip` files
- [Dashboard](dashboard.md) — the console at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
