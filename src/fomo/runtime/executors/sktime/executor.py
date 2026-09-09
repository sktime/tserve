"""sktime ``Executor``: load a forecaster, warmup, then fit/predict.

Registered as executor name ``sktime``. Registry ids such as ``naive``
are catalog keys consumed by ``load``, not this plugin name.

``to_response`` sets ``request_id=""``; server routes assign the real
id. String timestamps are converted with ``pandas.to_datetime``;
already-valid sktime indexes are left unchanged.

See Also
--------
fomo.runtime.executors.sktime.converters.from_request
    Maps ``CoercedPredictRequest`` onto ``y``, ``X``, ``X_future``,
    ``fh``.
fomo.types.models.CoercedPredictRequest
    Field semantics for ``predict``.
"""

from typing import Any

import pandas as pd

from fomo.runtime.executors.base import Executor
from fomo.runtime.executors.plugins import register
from fomo.runtime.executors.sktime.converters import from_request, to_response
from fomo.runtime.registry import SKTIME_REGISTRY
from fomo.types import CoercedPredictRequest, CoercedPredictResponse, ModelInfo

MISSING_DEPS_MESSAGE = (
    "Model {model!r} could not be loaded: its sktime forecaster needs soft "
    "dependencies that are missing from, or incompatible with, this "
    "environment.\n\nOriginal error: {error}\n\nInstall the dependency extra "
    'that covers this model, e.g. `pip install "fomo[<extra>]"` or '
    "`uv sync --extra <extra>`, then load it again. The catalog lists the "
    "extra (and matching Docker tag) for every model id: "
    "https://fomo.readthedocs.io/en/latest/models/"
)


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

        The forecaster is checked against the environment with
        ``sktime.utils.dependencies._check_estimator_deps``, so an
        ``object`` or ``directory`` forecaster that constructs fine but
        cannot run here is rejected at load time too.

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
        ModuleNotFoundError
            If the forecaster needs soft dependencies this environment
            does not satisfy. Re-raised from the underlying sktime error
            with ``MISSING_DEPS_MESSAGE``, pointing at the catalog extra.
        Exception
            Other errors from ``sktime.registry.craft`` or
            ``sktime.base.load``.
        """
        from sktime.utils.dependencies import _check_estimator_deps

        self._info = info

        try:
            if info.source == "registry":
                from sktime.registry import craft

                self._forecaster = craft(SKTIME_REGISTRY[model]["spec"])

            if info.source == "object":
                self._forecaster = model

            if info.source == "directory":
                from sktime.base import load

                self._forecaster = load(model)

            # craft/load can succeed while the forecaster's soft deps are
            # absent, so check the built forecaster as well.
            _check_estimator_deps(self._forecaster)

        except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
                MISSING_DEPS_MESSAGE.format(model=info.id, error=error)
            ) from error

    def warmup(self) -> None:
        """Fit a dummy 3-row ``y`` and ``predict`` with ``fh=[1]``.

        The dummy frame is ``pandas.DataFrame({"y": [0, 1, 2, ..., 127]})``.
        """
        self._forecaster.fit(pd.DataFrame({"y": list(range(128))}), fh=[1])
        self._forecaster.predict()

    def predict(self, request: CoercedPredictRequest) -> CoercedPredictResponse:
        """Fit on the request, predict, optionally predict quantiles.

        Calls ``from_request``, then ``fit(y, X, fh)``, then
        ``predict(X_future, fh)``. A non-empty ``quantiles`` list also
        runs ``predict_quantiles(alpha, X_future, fh)``. ``to_response``
        sets ``request_id=""``; server routes overwrite that on the
        bytes path after predict.

        Parameters
        ----------
        request : CoercedPredictRequest
            Internal forecast input. See
            ``fomo.types.models.CoercedPredictRequest``.

        Returns
        -------
        CoercedPredictResponse
            Point predictions and optional flattened quantile table.

        Raises
        ------
        ValidationError
            If ``to_response`` cannot construct
            ``CoercedPredictResponse`` (empty prediction tables).
        Exception
            Errors from the wrapped sktime ``fit`` / ``predict`` /
            ``predict_quantiles`` call.
        """
        y, X, X_future, fh, quantiles = from_request(request)

        self._forecaster.fit(y=y, X=X, fh=fh)
        pred = self._forecaster.predict(X=X_future, fh=fh)
        pred_quantiles = None
        if quantiles:
            pred_quantiles = self._forecaster.predict_quantiles(
                alpha=quantiles, X=X_future, fh=fh
            )

        response: CoercedPredictResponse = to_response(
            pred, request, quantiles=pred_quantiles
        )
        return response
