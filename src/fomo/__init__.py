"""fomo — time-series foundation-model inference server.

Load models once at process start, then serve forecasts over HTTP or
the Python ``Client``. User-facing types live in ``fomo.types``;
runtime loading and executors live under ``fomo.runtime``; forecast
dispatch lives under ``fomo.scheduling``. Import ``Client`` from
``fomo.client`` and ``Server`` from ``fomo.server`` — this package
does not re-export them.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fomo")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
