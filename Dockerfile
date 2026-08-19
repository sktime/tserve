FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "--frozen", "fomo", "serve", "--host", "0.0.0.0", "--port", "8000", "--load-model", "dummy", "chronos2", "timesfm2.5", "moirai2", "kronos"]
