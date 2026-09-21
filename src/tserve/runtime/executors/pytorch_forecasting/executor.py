"""Stub pytorch-forecasting ``Executor`` (not implemented).

Registered as executor name ``pytorch-forecasting``. ``create_executor``
can construct an instance; ``load``, ``warmup``, and ``predict`` all
raise ``NotImplementedError``. This is not a registry model id.

See Also
--------
tserve.runtime.executors.base.Executor
    Contract this class does not yet fulfill.
"""

from typing import Any

from tserve.runtime.executors.base import Executor
from tserve.runtime.executors.plugins import register
from tserve.types import CoercedPredictRequest, CoercedPredictResponse, ModelInfo


@register("pytorch-forecasting")
class PytorchForecastingExecutor(Executor):
    """Placeholder executor; every method raises ``NotImplementedError``."""

    def load(self, info: ModelInfo, model: Any) -> None:
        """Raise ``NotImplementedError`` (executor is not implemented).

        Parameters
        ----------
        info : ModelInfo
            Unused except ``info.id`` in the error message.
        model : any
            Unused.

        Raises
        ------
        NotImplementedError
            Always. Message includes ``info.id``.
        """
        raise NotImplementedError(
            f"pytorch-forecasting executor is not implemented yet (model {info.id!r})"
        )

    def warmup(self) -> None:
        """Raise ``NotImplementedError`` (executor is not implemented).

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("pytorch-forecasting executor is not implemented yet")

    def predict(self, request: CoercedPredictRequest) -> CoercedPredictResponse:
        """Raise ``NotImplementedError`` (executor is not implemented).

        Parameters
        ----------
        request : CoercedPredictRequest
            Unused except ``request.model`` in the error message.

        Returns
        -------
        CoercedPredictResponse
            Never returns; declared to match ``Executor.predict``.

        Raises
        ------
        NotImplementedError
            Always. Message includes ``request.model``.
        """
        raise NotImplementedError(
            "pytorch-forecasting executor is not implemented yet "
            f"(model {request.model!r})"
        )
