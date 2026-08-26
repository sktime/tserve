FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Always `--extra server --extra sktime-lite` so CMD can load naive.
# Add heavier extras at build time, e.g.
#   docker build --build-arg FOMO_EXTRAS=sktime .
#   docker build --build-arg FOMO_EXTRAS=pytorch-forecasting .
ARG FOMO_EXTRAS=""
RUN extras="" \
 && for extra in $FOMO_EXTRAS; do extras="$extras --extra $extra"; done \
 && uv sync --no-dev --extra server --extra sktime-lite $extras

EXPOSE 8000
ENTRYPOINT ["uv", "run", "fomo", "serve", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--load-models", "naive"]
