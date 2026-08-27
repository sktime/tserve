"""Transports used by ``Client``.

``BaseTransport`` is the ABC. ``HttpTransport`` is the implemented
subclass and the default ``Client`` constructs.

See Also
--------
fomo.client.transports.base.BaseTransport
    Abstract interface for forecast and status calls.
fomo.client.transports.http.HttpTransport
    HTTP implementation.
"""

from fomo.client.transports.base import BaseTransport
from fomo.client.transports.http import HttpTransport

__all__ = ["BaseTransport", "HttpTransport"]
