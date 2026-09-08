"""HTTP inference server for FoMo.

FoMo is a time-series foundation-model inference server. ``Server``
bootstraps a runtime, wraps it in a FastAPI app titled ``"FoMo"``, and
serves the routes in ``fomo.server.routes``. CLI ``fomo serve``
constructs ``Server`` and calls ``run``.

``ModelInfo`` is re-exported so listing rows can be imported from this
package.

See Also
--------
fomo.server.serve.Server
    Process wrapper around FastAPI and ``bootstrap``.
fomo.server.routes
    ``GET /health``, ``GET /models``, ``GET /stats``, and predict
    POST endpoints.
fomo.cli.main.main
    argparse entry that builds ``Server`` from ``fomo serve`` flags.
"""

from fomo.server.serve import Server
from fomo.types import ModelInfo

__all__ = ["ModelInfo", "Server"]
