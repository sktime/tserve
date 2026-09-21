"""HTTP inference server.

``Server`` always loads ``naive`` as a test baseline, plus extra models you
name for real forecasts, then serves a dashboard at ``/`` and OpenAPI at
``/docs``. CLI ``tserve serve`` constructs this class and calls ``run``.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from uvicorn.logging import DefaultFormatter

from tserve.logging.utils import paint
from tserve.runtime.bootstrap import Runtime, bootstrap
from tserve.server.routes import router

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "naive"


def _includes_default_model(model: list[str | Path | tuple[str, Any]]) -> bool:
    """Return whether ``model`` already names the always-loaded ``naive`` id."""
    for item in model:
        if item == _DEFAULT_MODEL:
            return True
        if isinstance(item, Path) and item.stem == _DEFAULT_MODEL:
            return True
        if isinstance(item, tuple) and item[0] == _DEFAULT_MODEL:
            return True
    return False


class Server:
    """Run a TServe inference HTTP server.

    Parameters
    ----------
    model : list of str or (str, object), optional
        Extra registry ids to load, ``(id, estimator)`` pairs, or
        ``(id, craft spec)`` string pairs. ``naive`` is always loaded as
        a test baseline. Default ``[]`` loads only ``naive``. When
        ``models_dir`` is set, matching ``.zip`` stems already in this
        list are loaded from disk.
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
        Unknown registry id, empty craft spec, non-zip path, or
        duplicate id.
    TypeError
        ``(id, object)`` whose object is neither a craft spec string
        nor a sktime ``BaseForecaster``.
    ImportError
        Executor extra is not installed.

    Examples
    --------
    >>> from tserve.server import Server
    >>> Server(host="127.0.0.1", port=8000).run()
    >>> Server(
    ...     model=[
    ...         "chronos-bolt",
    ...         ("drift", 'NaiveForecaster(strategy="drift")'),
    ...     ]
    ... )

    Notes
    -----
    ``naive`` is always loaded as a test baseline. Extra ids in ``model``
    load alongside it for real forecasts.

    See Also
    --------
    [Install and serve](../server/index.md)
        Installation, startup options, and server URLs.
    [Docker](../server/docker.md)
        Image defaults, tags, and container arguments.
    [Models catalog](../models/index.md)
        Registry ids and required family extras.
    [Live objects](../server/live-objects.md)
        In-process ``(id, estimator)`` pairs.
    [Craft specs](../server/craft-specs.md)
        ``(id, spec)`` pairs and CLI ``id=spec``.
    [Dashboard](../server/dashboard.md)
        Browser interface served by ``app`` at ``GET /``.
    """

    def __init__(
        self,
        model: list[str | Path | tuple[str, Any]] | None = None,
        models_dir: str | Path | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        """Construct a Server."""
        self.model = list(model) if model is not None else []
        self.models_dir = Path(models_dir) if models_dir is not None else None
        self.host = host
        self.port = port
        self.log_level = log_level

        # load model paths from `models_dir`
        # for only the selected ones in model
        if self.models_dir is not None:
            for model_path in self.models_dir.iterdir():
                name = model_path.stem
                if name in self.model:
                    self.model[self.model.index(name)] = model_path

        if not _includes_default_model(self.model):
            self.model = [_DEFAULT_MODEL, *self.model]

        # configure before bootstrap, so warmup progress is visible.
        # uvicorn's formatter makes TServe lines look like uvicorn's own;
        # the "tserve" logger only, to keep other libraries' records out.
        tserve_logger = logging.getLogger("tserve")
        tserve_logger.setLevel(self.log_level.upper())
        if not tserve_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(DefaultFormatter("%(levelprefix)s %(message)s"))
            tserve_logger.addHandler(handler)

        self.runtime: Runtime = bootstrap(self.model)
        self.app = FastAPI(title="TServe")
        self.app.state.runtime = self.runtime
        self.app.include_router(router)

    @property
    def url(self) -> str:
        """Return ``http://{host}:{port}``.

        See Also
        --------
        [Install and serve](../server/index.md)
            Bind addresses, ports, and published routes.
        """
        return f"http://{self.host}:{self.port}"

    def run(self) -> None:
        """Serve ``self.app`` with uvicorn.

        Blocks until the process exits.

        See Also
        --------
        [From source](../server/source.md)
            Run the server from Python or ``tserve serve``.
        [HTTP API](../reference/http.md)
            Routes exposed by the running app.
        [Dashboard](../server/dashboard.md)
            Browser interface at ``GET /``.
        """
        logger.info(paint("Starting TServe", "1"))
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
