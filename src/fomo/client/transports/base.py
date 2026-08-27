"""Abstract transport used by the FoMo client.

FoMo is a time-series foundation-model inference server. This module
defines ``BaseTransport`` as an ABC. ``HttpTransport`` is the only
concrete subclass today. ``Client`` accepts ``BaseTransport | None``.

See Also
--------
fomo.client.transports.http.HttpTransport
    httpx implementation that posts Arrow IPC to ``/forecast/bytes``.
"""

from abc import ABC, abstractmethod

from fomo.types import HealthResult, ModelsResult, StatsResult


class BaseTransport(ABC):
    """Send encoded forecasts and call the status endpoints.

    Subclasses own the wire (HTTP, and later other transports). They do
    not coerce frames; ``Client`` runs the wire converters and passes
    metadata plus Arrow IPC blobs into ``forecast``.
    """

    @abstractmethod
    def forecast(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]:
        """Send an encoded forecast and return the unpacked envelope.

        Parameters
        ----------
        metadata : dict
            JSON-serializable forecast fields (no frames).
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``history``, optional ``future`` /
            ``static``).

        Returns
        -------
        metadata : dict
            Response metadata from the envelope ``response`` part.
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``predictions``, optional
            ``quantiles``).
        """

    @abstractmethod
    def health(self) -> HealthResult:
        """Return server health.

        Returns
        -------
        HealthResult
            Parsed status payload.
        """

    @abstractmethod
    def models(self) -> ModelsResult:
        """Return loaded models.

        Lists **loaded** models only.

        Returns
        -------
        ModelsResult
            Parsed listing of models currently loaded on the server.
        """

    @abstractmethod
    def stats(self) -> StatsResult:
        """Return process stats.

        Returns
        -------
        StatsResult
            Parsed process and per-model metrics.
        """

    @abstractmethod
    def close(self) -> None:
        """Release the underlying connection."""
