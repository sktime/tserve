"""Command-line entry for FoMo.

FoMo is a time-series foundation-model inference server. CLI
``fomo serve`` builds ``Server`` and calls ``run``. Import ``main``
from this package or invoke the console script.

See Also
--------
fomo.cli.main.main
    argparse driver.
fomo.server.serve.Server
    Process started by ``serve``.
"""

from fomo.cli.main import main

__all__ = ["main"]
