"""Abstract transport used by the TServe client.

A transport moves encoded predict payloads and status queries between
``Client`` and a TServe runtime. ``HttpTransport`` is the implemented
subclass. Transports do not coerce frames: ``Client`` runs the wire
converters and passes metadata plus named frame blobs into
``predict``.

See Also
--------
tserve.client.client.Client
    Builds the metadata/bytes payload this ABC consumes.
tserve.client.transports.http.HttpTransport
    Default HTTP subclass.
"""

from abc import ABC, abstractmethod

from tserve.types import HealthResult, ModelsResult, StatsResult


class BaseTransport(ABC):
    """Send encoded predictions and fetch health, models, and stats.

    ``predict`` takes JSON-serializable metadata and named Arrow IPC
    blobs (``past``, optional ``future`` / ``static``) and returns
    the same pair for the response (``predictions``, optional
    ``quantiles``). ``HttpTransport`` sends them over HTTP.
    """

    @abstractmethod
    def predict(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]:
        """Send an encoded predict request and return encoded predictions.

        Parameters
        ----------
        metadata : dict
            JSON-serializable predict fields (no frames).
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
