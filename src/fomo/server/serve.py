from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.server.config import ServerConfig
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
        self.config = ServerConfig.from_options(
            models=models,
            host=host,
            port=port,
            log_level=log_level,
        )
        self.runtime: Runtime = bootstrap(list(self.config.models))
        self.app = FastAPI(title="FoMo")
        self.app.state.runtime = self.runtime
        self.app.include_router(router)

    @property
    def host(self) -> str:
        return self.config.host

    @property
    def port(self) -> int:
        return self.config.port

    @property
    def models(self) -> list[str]:
        return list(self.config.models)

    @property
    def url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def run(self) -> None:
        logging.basicConfig(level=logging.INFO)
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
        )
