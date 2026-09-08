# Development

From a clone of [sktime/fomo](https://github.com/sktime/fomo). Python >= 3.12.

```bash
git clone https://github.com/sktime/fomo.git && cd fomo
```

=== "uv"

    ```bash
    uv sync --extra server --extra client --group dev --group docs
    ```

=== "pip"

    ```bash
    pip install -e ".[server,client,dev,docs]"
    ```

## Checks

```bash
make quality
make style
```

`quality` runs ruff, ty, and codespell. Tests live under `tests/` and `src/fomo/**/tests/`:

```bash
uv run pytest
```

## Docs

```bash
make docs
make docs-serve
```

`make docs` is `mkdocs build --strict`. The site config is `mkdocs.yml`. Read the Docs uses `.readthedocs.yaml` and the `docs` dependency group.

## Docker images

The build matrix is `docker-bake.hcl`. Default image name is `sktime/fomo`; override to match Docker Hub:

```bash
FOMO_IMAGE=geetu040/fomo docker buildx bake --push hub
FOMO_IMAGE=fomo docker buildx bake --set base.platform=linux/amd64 --load base
```

See [Docker](docker.md#build-from-this-repo).

## Layout

| path | |
| --- | --- |
| `src/fomo/cli` | `fomo serve` |
| `src/fomo/server` | FastAPI app, dashboard, routes |
| `src/fomo/client` | Python `Client` and HTTP transport |
| `src/fomo/types` | `ForecastRequest` / response models and wire converters |
| `src/fomo/runtime` | registry, bootstrap, executors |
| `src/fomo/scheduling` | dispatch by loaded model id |
