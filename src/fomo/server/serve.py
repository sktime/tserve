"""Build and run the FoMo FastAPI inference server.

``Server`` calls ``bootstrap`` on ``load_models`` (after optional
``models_dir`` path rewriting), attaches the runtime to
``app.state.runtime``, and includes ``routes.router``. ``run`` starts
uvicorn on ``host``/``port``.
"""

import logging
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.server.routes import router


class Server:
    """Run a FoMo inference HTTP server.

    FoMo is a time-series foundation-model inference server. CLI
    ``fomo serve`` constructs this class and calls ``run``.

    ``load_models`` entries start as registry ids (or ``(id, object)``
    tuples). When ``models_dir`` is set, the constructor iterates that
    directory; for each path whose stem is in ``load_models``, it
    replaces that string id with the ``Path`` so ``resolve_model``
    treats it as a directory ``.zip``. Default ``load_models=[]`` loads
    nothing.

    Then ``bootstrap(self.load_models)`` runs, a FastAPI app titled
    ``"FoMo"`` is created, ``app.state.runtime`` is set, and
    ``routes.router`` is included.

    Parameters
    ----------
    load_models : list of str or (str, object), default []
        Registry ids to load, or later rewritten to ``Path`` when
        ``models_dir`` contains a matching stem. Tuples pass an
        in-process object through to ``bootstrap``.
    models_dir : str or pathlib.Path, optional
        Directory to scan. When set, each path whose stem is in
        ``load_models`` replaces that string id with the ``Path``.
    host : str, default ``"127.0.0.1"``
        Bind address passed to ``uvicorn.run``.
    port : int, default 8000
        Bind port passed to ``uvicorn.run``.
    log_level : str, default ``"info"``
        Uvicorn log level. ``run`` still calls
        ``logging.basicConfig(level=logging.INFO)``.

    Attributes
    ----------
    load_models : list
        Specs passed to ``bootstrap`` after optional ``models_dir``
        rewriting.
    models_dir : pathlib.Path or None
        Directory being scanned, or ``None`` if unset.
    host : str
        Bind host.
    port : int
        Bind port.
    log_level : str
        Uvicorn log level.
    runtime : fomo.runtime.bootstrap.Runtime
        Result of ``bootstrap(self.load_models)``.
    app : fastapi.FastAPI
        App titled ``"FoMo"`` with ``state.runtime`` and ``router``.
    url : str
        ``http://{host}:{port}``.

    Raises
    ------
    ValueError
        If ``bootstrap`` / ``resolve_model`` / ``create_executor``
        reject a load spec (duplicate id, unknown registry id,
        non-zip path, unknown executor).
    TypeError
        If a ``(id, object)`` entry is not a sktime ``BaseForecaster``.
    ImportError
        If the executor extra is not installed.
    OSError
        If ``models_dir`` cannot be listed.

    Notes
    -----
    Forecast ``request.model`` is a **loaded model id**, not an
    executor plugin name (``sktime``, and so on).

    See Also
    --------
    fomo.runtime.bootstrap.bootstrap
        Loads executors and builds the scheduler.
    fomo.runtime.registry.resolver.resolve_model
        Interprets string ids vs ``Path`` vs object tuples.
    fomo.server.routes
        HTTP handlers mounted on ``app``.
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
        """Construct a Server.

        See the class docstring for parameters and attributes.
        """
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

        self.runtime: Runtime = bootstrap(self.load_models)
        self.app = FastAPI(title="FoMo")
        self.app.state.runtime = self.runtime
        self.app.include_router(router)

    @property
    def url(self) -> str:
        """Return the HTTP origin ``http://{host}:{port}``.

        Returns
        -------
        str
            ``f"http://{self.host}:{self.port}"``. No path prefix.
        """
        return f"http://{self.host}:{self.port}"

    def run(self) -> None:
        """Configure logging and serve ``self.app`` with uvicorn.

        Calls ``logging.basicConfig(level=logging.INFO)`` then
        ``uvicorn.run(self.app, host=..., port=..., log_level=...)``.
        Blocks until the server exits. ``KeyboardInterrupt`` is not
        caught here; CLI ``main`` maps it to exit code 0.
        """
        logging.basicConfig(level=logging.INFO)
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.log_level,
        )
