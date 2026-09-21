"""tserve — time-series foundation-model inference server.

Load models once at process start, then serve forecasts over HTTP or
the Python ``Client``. User-facing types live in ``tserve.types``;
runtime loading and executors live under ``tserve.runtime``; forecast
dispatch lives under ``tserve.scheduling``. Import ``Client`` from
``tserve.client`` and ``Server`` from ``tserve.server`` — this package
does not re-export them.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tserve")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
