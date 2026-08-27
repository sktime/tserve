"""Public Python client for a FoMo inference server.

FoMo is a time-series foundation-model inference server. Import
``Client`` from this package to send forecasts over the bytes path
and to call the status endpoints.

See Also
--------
fomo.client.client.Client
    High-level client: coerce, encode, POST ``/forecast/bytes``, decode.
fomo.client.transports.http.HttpTransport
    The only transport implementation today.
"""

from fomo.client.client import Client

__all__ = ["Client"]
