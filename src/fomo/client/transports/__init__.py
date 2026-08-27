"""HTTP transports used by ``Client``.

``BaseTransport`` is an ABC. The only concrete subclass today is
``HttpTransport``. ``Client`` accepts ``BaseTransport | None``.

See Also
--------
fomo.client.transports.base.BaseTransport
    Abstract interface for forecast and status calls.
fomo.client.transports.http.HttpTransport
    httpx transport that posts Arrow IPC to ``/forecast/bytes``.
"""

from fomo.client.transports.base import BaseTransport
from fomo.client.transports.http import HttpTransport

__all__ = ["BaseTransport", "HttpTransport"]
