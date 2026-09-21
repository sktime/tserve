"""Public Python client for a TServe inference server.

TServe is a time-series foundation-model inference server. Import
``Client`` from this package to send forecasts and to query health,
loaded models, and stats. The default transport is ``HttpTransport``.

See Also
--------
tserve.client.client.Client
    High-level client: coerce, encode, send via the transport, decode.
tserve.client.transports.base.BaseTransport
    Abstract transport ``Client`` injects.
"""

from tserve.client.client import Client

__all__ = ["Client"]
