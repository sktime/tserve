"""Public Python client for a FoMo inference server.

FoMo is a time-series foundation-model inference server. Import
``Client`` from this package to send forecasts and to query health,
loaded models, and stats. The default transport is ``HttpTransport``.

See Also
--------
fomo.client.client.Client
    High-level client: coerce, encode, send via the transport, decode.
fomo.client.transports.base.BaseTransport
    Abstract transport ``Client`` injects.
"""

from fomo.client.client import Client

__all__ = ["Client"]
