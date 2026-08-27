"""Transport Protocol for the FoMo client.

FoMo is a time-series foundation-model inference server. This module
defines ``BaseTransport`` as a ``typing.Protocol``. Only
``HttpTransport`` implements it today. ``Client`` still annotates its
optional transport as ``HttpTransport | None``, not this Protocol.
"""

from typing import Protocol

from fomo.types import HealthResult, ModelsResult, StatsResult


class BaseTransport(Protocol):
    """Structural interface for forecast and status calls.

    Implementations send encoded forecast bytes and expose the
    ``/health``, ``/models``, and ``/stats`` endpoints.
    """

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
        ...

    def health(self) -> HealthResult:
        """Return server health. Delegates to ``GET /health``.

        Returns
        -------
        HealthResult
            Parsed status payload.
        """
        ...

    def models(self) -> ModelsResult:
        """Return loaded models. Delegates to ``GET /models``.

        Lists **loaded** models only.

        Returns
        -------
        ModelsResult
            Parsed listing of models currently loaded on the server.
        """
        ...

    def stats(self) -> StatsResult:
        """Return process stats. Delegates to ``GET /stats``.

        Returns
        -------
        StatsResult
            Parsed process and per-model metrics.
        """
        ...

    def close(self) -> None:
        """Release the underlying connection."""
        ...
