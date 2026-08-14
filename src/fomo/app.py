import logging

from fastapi import FastAPI

from fomo.api.routes import router
from fomo.runtime.bootstrap import bootstrap

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    application = FastAPI(title="FoMo")
    application.state.runtime = bootstrap()
    application.include_router(router)
    return application


app = create_app()
