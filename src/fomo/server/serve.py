from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.server.routes import router
from fomo.types import ModelInfo


class Server:
    def __init__(
        self,
        load_models: list[str | tuple[str, Any]] = [],
        models_dir: str | Path | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        self.load_models = load_models
        self.models_dir = Path(models_dir) if models_dir is not None else None
        self.host = host
        self.port = port
        self.log_level = log_level
        self.runtime: Runtime = bootstrap(self.load_models)
        self.app = FastAPI(title="FoMo")
        self.app.state.runtime = self.runtime
        self.app.include_router(router)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def run(self) -> None:
        logging.basicConfig(level=logging.INFO)
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.log_level,
        )
