"""Transports used by ``Client``.

``BaseTransport`` is the ABC. ``HttpTransport`` is the implemented
subclass and the default ``Client`` constructs.

See Also
--------
tserve.client.transports.base.BaseTransport
    Abstract interface for forecast and status calls.
tserve.client.transports.http.HttpTransport
    HTTP implementation.
"""

from tserve.client.transports.base import BaseTransport
from tserve.client.transports.http import HttpTransport

__all__ = ["BaseTransport", "HttpTransport"]
