"""Abstract executor contract used by bootstrap and the scheduler.

Implementations load one model artifact, warmup it, and ``predict`` from
a ``CoercedForecastRequest``. They do not accept user-facing
``ForecastRequest``.

See Also
--------
fomo.types.models.CoercedForecastRequest
    Field semantics for ``predict``.
fomo.runtime.executors.plugins.register
    Attach a concrete subclass to an executor name.
"""

from abc import ABC, abstractmethod
from typing import Any

from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


class Executor(ABC):
    """Load, warmup, and forecast for one loaded model.

    Bootstrap calls ``load`` then ``warmup`` once per selected model.
    The scheduler calls ``predict`` per request.
    """

    @abstractmethod
    def load(self, info: ModelInfo, model: Any) -> None:
        """Materialize the artifact described by ``info`` onto this instance.

        Parameters
        ----------
        info : ModelInfo
            Listing row (``id``, ``executor``, ``source``). ``source``
            selects how ``model`` is interpreted.
        model : any
            Registry id string, ``pathlib.Path`` to a zip, or an
            in-process forecaster object, as passed through from
            ``bootstrap``.
        """
        ...

    @abstractmethod
    def warmup(self) -> None:
        """Run a cheap fit/predict so the first real request is not cold."""
        ...

    @abstractmethod
    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        """Produce a coerced forecast for a loaded model.

        Parameters
        ----------
        request : CoercedForecastRequest
            Internal forecast input. See
            ``fomo.types.models.CoercedForecastRequest`` for fields.

        Returns
        -------
        CoercedForecastResponse
            Point predictions and optional quantiles as narwhals frames.
        """
        ...
