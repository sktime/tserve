"""Command-line entry for TServe.

TServe is a time-series foundation-model inference server. CLI
``tserve serve`` builds ``Server`` and calls ``run``. Import ``main``
from this package or invoke the console script.

See Also
--------
tserve.cli.main.main
    argparse driver.
tserve.server.serve.Server
    Process started by ``serve``.
"""

from tserve.cli.main import main

__all__ = ["main"]
