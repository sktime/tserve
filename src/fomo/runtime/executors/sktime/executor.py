"""sktime ``Executor``: load a forecaster, warmup, then fit/predict.

Registered as executor name ``sktime``. Registry ids such as ``naive``
are catalog keys consumed by ``load``, not this plugin name.

``context`` is required on the request but unused here. ``freq`` is
accepted; the convertor index uses ``freq="infer"``. ``params`` is
accepted and not applied.

See Also
--------
fomo.runtime.executors.sktime.convertors.from_request
    Maps ``CoercedForecastRequest`` onto ``y``, ``X``, ``X_future``,
    ``fh``.
fomo.types.models.CoercedForecastRequest
    Field semantics for ``predict``.
"""

from typing import Any

import pandas as pd

from fomo.runtime.executors.base import Executor
from fomo.runtime.executors.plugins import register
from fomo.runtime.executors.sktime.convertors import from_request, to_response
from fomo.runtime.registry import SKTIME_REGISTRY
from fomo.types import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


@register("sktime")
class SktimeExecutor(Executor):
    """Fit/predict wrapper around one sktime forecaster.

    Attributes
    ----------
    _info : ModelInfo or None
        Listing row set by ``load``, or ``None`` before load.
    _forecaster : any or None
        sktime forecaster set by ``load``, or ``None`` before load.
    """

    def __init__(self) -> None:
        """Set ``_info`` and ``_forecaster`` to ``None``. See the class docstring."""
        self._info: ModelInfo | None = None
        self._forecaster: Any = None

    def load(self, info: ModelInfo, model: Any) -> None:
        """Materialize a sktime forecaster from ``info.source``.

        * ``registry``: ``sktime.registry.craft(SKTIME_REGISTRY[model]["spec"])``
          where ``model`` is the ``load_models`` item string.
        * ``object``: use ``model`` as the forecaster.
        * ``directory``: ``sktime.base.load(model)`` (saved ``.zip`` path).

        Parameters
        ----------
        info : ModelInfo
            Must carry ``source`` ``registry``, ``object``, or
            ``directory``.
        model : any
            Registry id, in-process forecaster, or zip path, matching
            ``source``.

        Raises
        ------
        KeyError
            If ``source`` is ``registry`` and ``model`` is not a key of
            ``SKTIME_REGISTRY``.
        Exception
            Errors from ``sktime.registry.craft`` or
            ``sktime.base.load``.
        """
        self._info = info

        if info.source == "registry":
            from sktime.registry import craft

            self._forecaster = craft(SKTIME_REGISTRY[model]["spec"])

        if info.source == "object":
            self._forecaster = model

        if info.source == "directory":
            from sktime.base import load

            self._forecaster = load(model)

    def warmup(self) -> None:
        """Fit a dummy 3-row ``y`` and ``predict`` with ``fh=[1]``.

        The dummy frame is ``pandas.DataFrame({"y": [0.0, 1.0, 2.0]})``.
        """
        self._forecaster.fit(pd.DataFrame({"y": [0.0, 1.0, 2.0]}))
        self._forecaster.predict(fh=[1])

    def predict(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        """Fit on the request, predict, optionally predict quantiles.

        Calls ``from_request``, then ``fit(y, X, fh)``, then
        ``predict(X_future, fh)``. A non-empty ``quantiles`` list also
        runs ``predict_quantiles(alpha, X_future, fh)``. ``to_response``
        sets ``request_id=""``; server routes overwrite that on the
        bytes path after predict.

        Parameters
        ----------
        request : CoercedForecastRequest
            Internal forecast input. See
            ``fomo.types.models.CoercedForecastRequest``.

        Returns
        -------
        CoercedForecastResponse
            Point predictions and optional flattened quantile table.

        Raises
        ------
        ValueError
            If ``request.series_id`` is set (panel not supported;
            raised by ``from_request``).
        ValidationError
            If ``to_response`` cannot construct
            ``CoercedForecastResponse`` (empty prediction tables).
        Exception
            Errors from the wrapped sktime ``fit`` / ``predict`` /
            ``predict_quantiles`` call.

        Notes
        -----
        ``context``, ``freq``, and ``params`` are not read. Panel
        ``series_id`` is rejected in ``from_request``.
        """
        y, X, X_future, fh, quantiles = from_request(request)

        self._forecaster.fit(y=y, X=X, fh=fh)
        pred = self._forecaster.predict(X=X_future, fh=fh)
        pred_quantiles = None
        if quantiles:
            pred_quantiles = self._forecaster.predict_quantiles(
                alpha=quantiles, X=X_future, fh=fh
            )

        response: CoercedForecastResponse = to_response(pred, request, quantiles=pred_quantiles)
        return response
