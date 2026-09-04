"""HTTP inference server.

``Server`` loads the models you name, then serves forecasts, a
dashboard at ``/``, and OpenAPI at ``/docs``. CLI ``fomo serve``
constructs this class and calls ``run``.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from uvicorn.logging import DefaultFormatter

from fomo.logging.utils import paint
from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.server.routes import router

logger = logging.getLogger(__name__)


class Server:
    """Run a FoMo inference HTTP server.

    Parameters
    ----------
    load_models : list of str or (str, object), optional
        Registry ids to load, or ``(id, estimator)`` pairs. Default
        ``[]`` loads nothing. When ``models_dir`` is set, matching
        ``.zip`` stems already in this list are loaded from disk.
    models_dir : str or pathlib.Path, optional
        Directory of saved sktime ``.zip`` files. Not loaded wholesale.
    host : str, default ``"127.0.0.1"``
        Bind address.
    port : int, default 8000
        Bind port.
    log_level : str, default ``"info"``
        Uvicorn log level.

    Attributes
    ----------
    url : str
        ``http://{host}:{port}``.
    app : fastapi.FastAPI
        The ASGI app (dashboard, JSON, OpenAPI).

    Raises
    ------
    ValueError
        Unknown registry id, non-zip path, or duplicate id.
    TypeError
        ``(id, object)`` whose object is not a sktime ``BaseForecaster``.
    ImportError
        Executor extra is not installed.

    Examples
    --------
    >>> from fomo.server import Server
    >>> Server(load_models=["naive"], host="127.0.0.1", port=8000).run()
    """

    def __init__(
        self,
        load_models: list[str | Path | tuple[str, Any]] | None = None,
        models_dir: str | Path | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        """Construct a Server."""
        self.load_models = list(load_models) if load_models is not None else []
        self.models_dir = Path(models_dir) if models_dir is not None else None
        self.host = host
        self.port = port
        self.log_level = log_level

        # load model paths from `models_dir`
        # for only the selected ones in load_models
        if self.models_dir is not None:
            for model_path in self.models_dir.iterdir():
                name = model_path.stem
                if name in self.load_models:
                    self.load_models[self.load_models.index(name)] = model_path

        # configure before bootstrap, so warmup progress is visible.
        # uvicorn's formatter makes FoMo lines look like uvicorn's own;
        # the "fomo" logger only, to keep other libraries' records out.
        fomo_logger = logging.getLogger("fomo")
        fomo_logger.setLevel(self.log_level.upper())
        if not fomo_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(DefaultFormatter("%(levelprefix)s %(message)s"))
            fomo_logger.addHandler(handler)

        self.runtime: Runtime = bootstrap(self.load_models)
        self.app = FastAPI(title="FoMo")
        self.app.state.runtime = self.runtime
        self.app.include_router(router)

    @property
    def url(self) -> str:
        """Return ``http://{host}:{port}``."""
        return f"http://{self.host}:{self.port}"

    def run(self) -> None:
        """Serve ``self.app`` with uvicorn. Blocks until the process exits."""
        logger.info(paint("Starting FoMo", "1"))
        for label, path in (
            ("Dashboard", "/"),
            ("Swagger UI", "/docs"),
            ("ReDoc", "/redoc"),
        ):
            logger.info(
                f"  {paint(f'{label:<11}', '2')} {paint(f'{self.url}{path}', '1;36')}"
            )

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.log_level,
        )
