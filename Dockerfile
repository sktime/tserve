# we avoid using python3.13-bookworm-slim here
# see https://github.com/sktime/fomo/issues/92
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# `server` and `sktime` are always in, so CMD can load naive. Heavier extras
# come from the build arg, one word each, e.g.
#   docker build --build-arg FOMO_EXTRAS=hub .
#   docker build --build-arg FOMO_EXTRAS="chronos gpu" .
ARG FOMO_EXTRAS=""
# The cache mount keeps uv's wheels out of the image (several GB on a GPU sync)
# while still reusing them across rebuilds. printf repeats its format once per
# extra, turning `chronos gpu` into `--extra chronos --extra gpu`.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev $(printf -- '--extra %s ' server sktime $FOMO_EXTRAS)

EXPOSE 8000
ENTRYPOINT ["uv", "run", "--no-sync", "fomo", "serve", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--load-models", "naive"]
