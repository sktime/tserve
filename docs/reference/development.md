# Development

Working on TServe itself, from a clone of [sktime/tserve](https://github.com/sktime/tserve). Python >= 3.12.

```bash
git clone https://github.com/sktime/tserve.git && cd tserve
```

`server` and `client` are enough for the test suite and the docs; add a [family extra](../models/index.md#dependencies) only to run real models locally.

=== "uv"

    ```bash
    uv sync --extra server --extra client --group dev --group docs
    ```

=== "pip"

    ```bash
    pip install -e ".[server,client,dev,docs]"
    ```

The `dev` and `docs` dependency groups mirror the same-named extras, so both installers get the same packages.

## Checks

```bash
make quality
make style
```

`quality` runs `ruff check`, `ruff format --check`, `ty check`, and `codespell`; `style` is the fixing pass of the first two. Docstrings follow the numpy convention and ruff's `D` rules, currently enforced on `cli`, `client`, and `types`.

Pre-commit runs the same tools plus whitespace, line-ending, and YAML/TOML hooks, and CI runs it over every file:

```bash
uv run --group dev pre-commit install
uv run --group dev pre-commit run --files docs/reference/errors.md
```

## Tests

```bash
uv run pytest
```

Unit tests sit next to the code in `src/tserve/**/tests/`; `tests/` holds the end-to-end pass. Everything runs in-process through FastAPI's `TestClient` against `naive`, so no server, network, or GPU is needed.

## Docs

```bash
make docs
make docs-serve
```

`make docs` is `mkdocs build --strict`, which is what CI and Read the Docs run (`.readthedocs.yaml` sets `fail_on_warning: true`), so a broken link or a bad cross-reference fails the build. Pages live in `docs/`, the nav and Material options in `mkdocs.yml`, and tooltip expansions in `includes/abbreviations.md`. `docs-serve` reloads on changes to `docs/`, `includes/`, and `src/` — the last one matters because [Python API](api.md) is generated from docstrings.

## Docker images

`Dockerfile` always installs `--extra server --extra sktime` and adds whatever `TSERVE_EXTRAS` names, which is how one file produces every tag. `docker-bake.hcl` holds the published matrix: one target per tag, plus `cpu` and `gpu` groups, with `TSERVE_IMAGE` defaulting to `sktime/tserve`.

```bash
TSERVE_IMAGE=sktime/tserve docker buildx bake --push hub
TSERVE_IMAGE=local/tserve docker buildx bake --set hub.platform=linux/amd64 --load hub
```

Targets are `linux/amd64` plus `linux/arm64`, so a plain multi-platform bake needs a container builder and `--push`; pin one platform to `--load` into the local image store instead. Setting that builder up once per machine, and building single images by hand, is on [Docker](../server/docker.md#build-an-image-yourself).

## Layout

| path | |
| --- | --- |
| `src/tserve/cli` | `tserve` argument parsing |
| `src/tserve/server` | FastAPI app, routes, dashboard assets |
| `src/tserve/client` | `Client` and its HTTP transport |
| `src/tserve/types` | request/response models and the wire converters |
| `src/tserve/runtime` | registry, bootstrap, executors |
| `src/tserve/scheduling` | dispatch by loaded model |
| `src/tserve/logging` | stats collected for `GET /stats` |

How those pieces fit together is on [Overview](../overview.md).
