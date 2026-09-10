# we avoid using python3.13-bookworm-slim here
# see https://github.com/sktime/fomo/issues/92
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Always `--extra server --extra sktime` so CMD can load naive.
# Add heavier extras at build time, e.g.
#   docker build --build-arg FOMO_EXTRAS=hub .
#   docker build --build-arg FOMO_EXTRAS="chronos gpu" .
ARG FOMO_EXTRAS=""
RUN extras="" \
 && for extra in $FOMO_EXTRAS; do extras="$extras --extra $extra"; done \
 && uv sync --no-dev --extra server --extra sktime $extras

EXPOSE 8000
ENTRYPOINT ["uv", "run", "--no-sync", "fomo", "serve", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--load-models", "naive"]
