"""Abstract executor contract used by bootstrap and the scheduler.

Implementations load one model artifact, warmup it, and ``predict`` from
a ``CoercedPredictRequest``. They do not accept user-facing
``PredictRequest``.

See Also
--------
fomo.types.models.CoercedPredictRequest
    Field semantics for ``predict``.
fomo.runtime.executors.plugins.register
    Attach a concrete subclass to an executor name.
"""

from abc import ABC, abstractmethod
from typing import Any

from fomo.types import CoercedPredictRequest, CoercedPredictResponse, ModelInfo


class Executor(ABC):
    """Load, warmup, and predict for one loaded model.

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
    def predict(self, request: CoercedPredictRequest) -> CoercedPredictResponse:
        """Produce a coerced prediction for a loaded model.

        Parameters
        ----------
        request : CoercedPredictRequest
            Internal predict input. See
            ``fomo.types.models.CoercedPredictRequest`` for fields.

        Returns
        -------
        CoercedPredictResponse
            Point predictions and optional quantiles as narwhals frames.
        """
        ...
