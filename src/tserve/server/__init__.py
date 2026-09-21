"""HTTP inference server for TServe.

TServe is a time-series foundation-model inference server. ``Server``
bootstraps a runtime, wraps it in a FastAPI app titled ``"TServe"``, and
serves the routes in ``tserve.server.routes``. CLI ``tserve``
constructs ``Server`` and calls ``run``.

``ModelInfo`` is re-exported so listing rows can be imported from this
package.

See Also
--------
tserve.server.serve.Server
    Process wrapper around FastAPI and ``bootstrap``.
tserve.server.routes
    ``GET /health``, ``GET /models``, ``GET /stats``, and predict
    POST endpoints.
tserve.cli.main.main
    argparse entry that builds ``Server`` from ``tserve`` flags.
"""

from tserve.server.serve import Server
from tserve.types import ModelInfo

__all__ = ["ModelInfo", "Server"]
