FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN uv sync --no-dev --extra server --extra sktime

EXPOSE 8000
ENTRYPOINT ["uv", "run", "fomo", "serve", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--load-models", "naive"]
