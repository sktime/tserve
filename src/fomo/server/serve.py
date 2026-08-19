from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.runtime.config import DEFAULT_MODELS
from fomo.server.routes import router


class Server:
    def __init__(
        self,
        load_model: list[str] | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        self.load_model = list(load_model) if load_model is not None else list(DEFAULT_MODELS)
        self.host = host
        self.port = port
        self.log_level = log_level
        self.runtime: Runtime = bootstrap(self.load_model)
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
