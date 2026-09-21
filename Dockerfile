# we avoid using python3.13-bookworm-slim here
# see https://github.com/sktime/tserve/issues/92
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

WORKDIR /app

# Cache mount lives on another filesystem, so copy instead of hardlinking.
# UV_PYTHON_DOWNLOADS=0 uses the image Python so the venv shebang still
# works after we copy it onto python:3.13-slim-trixie.
# uv's HTTP read timeout is 30s by default; a full bake saturates the network
# and large wheels (torch, CUDA) then fail.
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_HTTP_TIMEOUT=300 \
    UV_HTTP_RETRIES=10

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 git \
    && rm -rf /var/lib/apt/lists/*

# `server` and `sktime` are always in, so the process can load naive. Heavier extras
# come from the build arg, one word each, e.g.
#   docker build --build-arg TSERVE_EXTRAS=hub .
#   docker build --build-arg TSERVE_EXTRAS="chronos gpu" .
ARG TSERVE_EXTRAS=""

# Resolve and install third-party deps from pyproject.toml only. Source changes
# then do not rebuild this layer. uv.lock is not tracked, so this is not
# `--frozen` / `--locked`. printf repeats `--extra` once per remaining word.
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project --no-editable \
        $(printf -- '--extra %s ' server sktime $TSERVE_EXTRAS)

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable \
        $(printf -- '--extra %s ' server sktime $TSERVE_EXTRAS)

# Runtime image: no uv, no git, no source tree. `--no-editable` baked tserve
# into the venv, so only `.venv` is copied. Python path must match the builder.
FROM python:3.13-slim-trixie

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
ENTRYPOINT ["tserve", "serve", "--host", "0.0.0.0", "--port", "8000"]
