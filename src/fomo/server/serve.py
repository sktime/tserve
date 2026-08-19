from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.runtime.config import configured_models
from fomo.server.routes import router


class Server:
    def __init__(
        self,
        models: list[str] | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        self.models = list(models) if models is not None else configured_models()
        self.host = host
        self.port = port
        self.log_level = log_level
        self.runtime: Runtime = bootstrap(self.models)
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
