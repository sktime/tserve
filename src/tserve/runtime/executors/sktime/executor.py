"""sktime ``Executor``: load a forecaster, warmup, then fit/predict.

Registered as executor name ``sktime``. Registry ids such as ``naive``
are catalog keys consumed by ``load``, not this plugin name.

``to_response`` sets ``request_id=""``; server routes assign the real
id. String timestamps are converted with ``pandas.to_datetime``;
already-valid sktime indexes are left unchanged.

See Also
--------
tserve.runtime.executors.sktime.converters.from_request
    Maps ``CoercedPredictRequest`` onto ``y``, ``X``, ``X_future``,
    ``fh``.
tserve.types.models.CoercedPredictRequest
    Field semantics for ``predict``.
"""

from typing import Any

import pandas as pd

from tserve.runtime.executors.base import Executor
from tserve.runtime.executors.plugins import register
from tserve.runtime.executors.sktime.converters import from_request, to_response
from tserve.runtime.registry import SKTIME_REGISTRY
from tserve.types import CoercedPredictRequest, CoercedPredictResponse, ModelInfo

_CATALOG_URL = "https://tserve.readthedocs.io/en/latest/models/"


def _missing_dependency_message(model_id: str, error: ModuleNotFoundError) -> str:
    """Name the extra and Docker tag that cover ``model_id``, with install commands."""
    head = (
        f"Model {model_id!r} could not be loaded: its sktime forecaster "
        "needs soft dependencies that are missing from, or incompatible "
        f"with, this environment.\n\nOriginal error: {error}"
    )
    group = SKTIME_REGISTRY.get(model_id, {}).get("group") or ()
    if not group:
        return (
            f"{head}\n\nInstall the dependency extra that covers this model, "
            'e.g. `pip install "tserve[<extra>]"` or `uv sync --extra <extra>`, '
            "then load it again. The catalog lists the extra (and matching "
            f"Docker tag) for every model id: {_CATALOG_URL}"
        )

    extra = group[0]
    extras = ("server",) if extra == "server" else ("server", extra)
    tag = "base" if extra == "server" else extra
    tags = ", ".join(f":{'base' if name == 'server' else name}" for name in group)
    return "\n".join(
        [
            head,
            "",
            "Install a compatible extra, then load it again:",
            f"  uv sync {' '.join(f'--extra {name}' for name in extras)}",
            f'  pip install -e ".[{",".join(extras)}]"',
            "",
            "Or pull a matching image:",
            f"  docker run --rm -p 8000:8000 sktime/tserve:{tag} {model_id}",
            "",
            f"Compatible extras: {', '.join(group)}",
            f"Compatible tags: {tags}",
            "",
            f"The catalog has the full map: {_CATALOG_URL}",
        ]
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
          where ``model`` is the catalog id string.
        * ``craft``: ``sktime.registry.craft(model)`` where ``model`` is
          the user-supplied spec string. The result must be a
          ``BaseForecaster`` instance (``craft("NaiveForecaster")``
          returns a class and is rejected).
        * ``object``: use ``model`` as the forecaster.
        * ``directory``: ``sktime.base.load(model)`` (saved ``.zip`` path).

        The forecaster is checked against the environment with
        ``sktime.utils.dependencies._check_estimator_deps``, so an
        ``object`` or ``directory`` forecaster that constructs fine but
        cannot run here is rejected at load time too.

        Parameters
        ----------
        info : ModelInfo
            Must carry ``source`` ``registry``, ``craft``, ``object``,
            or ``directory``.
        model : any
            Registry id, craft spec string, in-process forecaster, or
            zip path, matching ``source``.

        Raises
        ------
        KeyError
            If ``source`` is ``registry`` and ``model`` is not a key of
            ``SKTIME_REGISTRY``.
        TypeError
            If ``source`` is ``craft`` and the spec does not produce a
            ``BaseForecaster`` instance.
        ModuleNotFoundError
            If the forecaster needs soft dependencies this environment
            does not satisfy. Re-raised from the underlying sktime error
            with the uv, pip, and Docker commands for this model id.
        Exception
            Other errors from ``sktime.registry.craft`` or
            ``sktime.base.load``.
        """
        from sktime.forecasting.base import BaseForecaster
        from sktime.utils.dependencies import _check_estimator_deps

        self._info = info

        try:
            if info.source == "registry":
                from sktime.registry import craft

                self._forecaster = craft(SKTIME_REGISTRY[model]["spec"], safe=True)
            elif info.source == "craft":
                from sktime.registry import craft

                self._forecaster = craft(model, safe=True)
                if not isinstance(self._forecaster, BaseForecaster):
                    raise TypeError(
                        f"craft spec for {info.id!r} must produce a sktime "
                        f"forecaster instance, got {type(self._forecaster).__name__}"
                    )
            elif info.source == "object":
                self._forecaster = model
            elif info.source == "directory":
                from sktime.base import load

                self._forecaster = load(model)

            # craft/load can succeed while the forecaster's soft deps are
            # absent, so check the built forecaster as well.
            _check_estimator_deps(self._forecaster)

        except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
                _missing_dependency_message(info.id, error)
            ) from error

    def warmup(self) -> None:
        """Fit a dummy 3-row ``y`` and ``predict`` with ``fh=[1]``.

        The dummy frame is ``pandas.DataFrame({"y": [0, 1, 2, ..., 127]})``.

        Raises
        ------
        RuntimeError
            If the forecaster cannot fit and predict the dummy series.
            Re-raised from the underlying sktime error, since a model
            that fails here would fail on every request.
        """
        model = self._info.id if self._info is not None else "unknown"

        try:
            self._forecaster.fit(pd.DataFrame({"y": list(range(128))}), fh=[1])
            self._forecaster.predict()

        except Exception as error:
            raise RuntimeError(
                f"Model {model!r} was loaded but failed to forecast a dummy "
                "128-row series during warmup, so it would fail on every "
                f"request.\n\nOriginal error: {error}\n\nThe forecaster itself "
                "was built, so this is usually the environment rather than the "
                "model id: a dependency version it cannot work with, or a "
                "device it cannot reach. Installing the catalog's extra for "
                "this model pins versions known to work: "
                "https://tserve.readthedocs.io/en/latest/models/"
            ) from error

    def predict(self, request: CoercedPredictRequest) -> CoercedPredictResponse:
        """Fit on the request, predict, optionally predict quantiles.

        Calls ``from_request``, then ``fit(y, X, fh)``, then
        ``predict(X_future, fh)``. A non-empty ``quantiles`` list also
        runs ``predict_quantiles(alpha, X_future, fh)``. ``to_response``
        sets ``request_id=""``; server routes overwrite that on the
        bytes path after predict.

        ``quantiles`` against a forecaster whose
        ``capability:pred_int`` tag is false is rejected before
        ``predict_quantiles`` is called, so that case carries no
        estimator message at all.

        Parameters
        ----------
        request : CoercedPredictRequest
            Internal forecast input. See
            ``tserve.types.models.CoercedPredictRequest``.

        Returns
        -------
        CoercedPredictResponse
            Point predictions and optional flattened quantile table.

        Raises
        ------
        ValidationError
            If ``to_response`` cannot construct
            ``CoercedPredictResponse`` (empty prediction tables).
        RuntimeError
            If the point forecast (``fit`` then ``predict``) raised, if
            ``quantiles`` was sent to a forecaster that cannot produce
            them, or if ``predict_quantiles`` raised. The message says
            which step failed and what usually causes it, and quotes the
            estimator's own message under ``Original error:``.
        """
        # 1. Parse Request
        y, X, X_future, fh, quantiles = from_request(request)
        pred = None
        pred_quantiles = None

        # 2. Get Point Forecast
        try:
            self._forecaster.fit(y=y, X=X, fh=fh)
            pred = self._forecaster.predict(X=X_future, fh=fh)
        except Exception as error:
            raise RuntimeError(
                f"Model {request.model!r} failed to forecast {request.fh} "
                f"step(s) ahead from the {len(y)} row(s) in past.\n\nOriginal "
                f"error: {error}\n\nCheck the request against what this model "
                "supports. The catalog records the context, horizon, and "
                "capabilities of every model: "
                "https://tserve.readthedocs.io/en/latest/models/"
            ) from error

        # 3. Get Quantile Forecasts
        if quantiles and not self._forecaster.get_tag("capability:pred_int"):
            raise RuntimeError(
                f"Model {request.model!r} cannot return quantile predictions, "
                f"so the requested quantiles {quantiles} are unavailable.\n\n"
                "Drop `quantiles` from the request to get point forecasts "
                "only, or load a model that supports them. The catalog marks "
                "quantile support for every family: "
                "https://tserve.readthedocs.io/en/latest/models/"
            )
        elif quantiles:
            try:
                pred_quantiles = self._forecaster.predict_quantiles(
                    alpha=quantiles, X=X_future, fh=fh
                )
            except Exception as error:
                raise RuntimeError(
                    f"Model {request.model!r} returned its point forecast but "
                    f"failed on the requested quantiles {quantiles}.\n\n"
                    f"Original error: {error}\n\nDrop `quantiles` to keep just "
                    "the point forecast, or check what this model supports. "
                    "The catalog records the quantile support of every model: "
                    "https://tserve.readthedocs.io/en/latest/models/"
                ) from error

        # 4. Create Response
        response: CoercedPredictResponse = to_response(
            pred, request, quantiles=pred_quantiles
        )

        return response
