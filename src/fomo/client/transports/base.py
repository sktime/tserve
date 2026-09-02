"""Abstract transport used by the FoMo client.

A transport moves encoded forecast payloads and status queries between
``Client`` and a FoMo runtime. ``HttpTransport`` is the implemented
subclass. Transports do not coerce frames: ``Client`` runs the wire
converters and passes metadata plus named frame blobs into
``forecast``.

See Also
--------
fomo.client.client.Client
    Builds the metadata/bytes payload this ABC consumes.
fomo.client.transports.http.HttpTransport
    Default HTTP subclass.
"""

from abc import ABC, abstractmethod

from fomo.types import HealthResult, ModelsResult, StatsResult


class BaseTransport(ABC):
    """Send encoded forecasts and fetch health, models, and stats.

    ``forecast`` takes JSON-serializable metadata and named Arrow IPC
    blobs (``past``, optional ``future`` / ``static``) and returns
    the same pair for the response (``predictions``, optional
    ``quantiles``). ``HttpTransport`` sends them over HTTP.
    """

    @abstractmethod
    def forecast(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]:
        """Send an encoded forecast and return encoded predictions.

        Parameters
        ----------
        metadata : dict
            JSON-serializable forecast fields (no frames).
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``past``, optional ``future`` /
            ``static``).

        Returns
        -------
        metadata : dict
            JSON-serializable response fields (no frames).
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``predictions``, optional
            ``quantiles``).
        """

    @abstractmethod
    def health(self) -> HealthResult:
        """Return runtime health.

        Returns
        -------
        HealthResult
            Parsed status payload.
        """

    @abstractmethod
    def models(self) -> ModelsResult:
        """Return loaded models.

        Lists **loaded** models only, not the full registry catalog.

        Returns
        -------
        ModelsResult
            Parsed listing of models currently loaded.
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
        """Release the underlying connection or other resources."""
