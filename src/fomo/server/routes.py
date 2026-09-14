"""HTTP routes for health, listing, stats, and predict.

Mounted on the FastAPI app by ``Server``. Predict handlers use *wire*
converters in ``fomo.types.converters`` (``coerce_request``,
``decode_request``, ``encode_response``, ``pack_envelope``), not the
sktime *converters* in ``fomo.runtime.executors.sktime.converters``.

``GET /`` serves the browser dashboard from ``fomo/server/static``,
which is also mounted at ``/static``. It drives the JSON endpoints only
(``/health``, ``/models``, ``/stats``, ``POST /predict``).

``request.model`` is a loaded model id. ``request_id`` is assigned in
these handlers: the JSON path puts a UUID on ``PredictResponse``
directly; the bytes path overwrites
``CoercedPredictResponse.request_id`` after predict (sktime
``to_response`` sets ``""``). FoMo has no custom exception types;
predict failures become ``HTTPException`` 400.
"""

import json
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fomo.types import (
    HealthResult,
    ModelsResult,
    PredictRequest,
    PredictResponse,
    StatsResult,
)
from fomo.types.converters import (
    coerce_request,
    decode_request,
    encode_response,
    pack_envelope,
)

_ENVELOPE_CONTENT_TYPE = "application/vnd.fomo.predict+arrow"
_STATIC_DIR = Path(__file__).parent / "static"


router = APIRouter()
router.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@router.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    """Serve the dashboard shell as ``GET /``.

    Returns ``static/index.html``; the page then calls the JSON
    endpoints (``GET /health``, ``GET /models``, ``GET /stats``,
    ``POST /predict``) from the browser. ``POST /predict/bytes`` is
    not used by the dashboard.

    Returns
    -------
    fastapi.responses.FileResponse
        ``static/index.html`` with media type ``text/html``.

    See Also
    --------
    fomo.server.serve.Server
        Includes this router on the FastAPI app.
    """
    return FileResponse(_STATIC_DIR / "index.html", media_type="text/html")


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    """Serve the sktime icon as ``GET /favicon.ico``.

    Browsers request this path directly, so it is served alongside the
    ``/static/favicon.svg`` copy the page links.

    Returns
    -------
    fastapi.responses.FileResponse
        ``static/favicon.svg`` with media type ``image/svg+xml``.
    """
    return FileResponse(_STATIC_DIR / "favicon.svg", media_type="image/svg+xml")


@router.get("/health", response_model=HealthResult, response_model_exclude_none=True)
def health() -> HealthResult:
    """Return process liveness as ``GET /health``.

    Always returns ``HealthResult(status="ok")`` today. ``HealthError``
    is a nested payload model on ``HealthResult.error``, not an
    exception this handler raises.

    Returns
    -------
    HealthResult
        ``status="ok"`` with ``error`` omitted.

    See Also
    --------
    fomo.types.models.HealthResult
        Response schema, including unused ``error``.
    fomo.types.models.HealthError
        Payload nested under ``HealthResult.error``, never raised.
    """
    return HealthResult(status="ok")


@router.get("/models", response_model=ModelsResult)
def models(request: Request) -> ModelsResult:
    """List **loaded** models as ``GET /models``.

    Delegates to ``runtime.loaded_models()``. This is not the full
    registry catalog: ids never passed to ``load_models`` /
    ``--load-models`` do not appear.

    Parameters
    ----------
    request : fastapi.Request
        Used to read ``app.state.runtime``.

    Returns
    -------
    ModelsResult
        Currently loaded models (may be empty).

    See Also
    --------
    fomo.types.models.ModelsResult
        Response schema.
    fomo.runtime.bootstrap.Runtime.loaded_models
        Source of the listing.
    """
    return request.app.state.runtime.loaded_models()


@router.get("/stats", response_model=StatsResult)
def stats(request: Request) -> StatsResult:
    """Return runtime metrics as ``GET /stats``.

    Builds ``StatsResult.model_validate(runtime.stats.snapshot())``.

    Parameters
    ----------
    request : fastapi.Request
        Used to read ``app.state.runtime``.

    Returns
    -------
    StatsResult
        Uptime, memory probes, and per loaded-model-id metrics.

    See Also
    --------
    fomo.types.models.StatsResult
        Response schema.
    fomo.logging.stats.Stats.snapshot
        Dict this handler validates.
    """
    return StatsResult.model_validate(request.app.state.runtime.stats.snapshot())


@router.get("/predict", include_in_schema=False)
def predict_get() -> None:
    """Reject ``GET /predict`` with a pointer at POST."""
    raise HTTPException(
        status_code=405,
        detail="GET /predict is not supported; send a JSON body with POST /predict.",
        headers={"Allow": "POST"},
    )


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, http_request: Request) -> PredictResponse:
    """Run a JSON ``POST /predict``.

    Assigns a UUID ``request_id``, coerces the body with
    ``coerce_request``, then ``scheduler.run``. On success, returns
    ``PredictResponse`` with ``predictions`` (and ``quantiles`` when
    present) as ``to_dict(as_series=False)``, ``model`` from the
    executor response, and the UUID. Handler failures (coerce or
    predict) become ``HTTPException`` 400 with ``detail``
    ``{error: str(exc), code: "request_failed", request_id}``. Invalid
    JSON bodies that fail ``PredictRequest`` validation are rejected
    by FastAPI as 422 before this handler runs.

    ``request.model`` is a loaded model id, not an executor name.

    Parameters
    ----------
    request : PredictRequest
        JSON body. See that class for fields.
    http_request : fastapi.Request
        Used to read ``app.state.runtime.scheduler``.

    Returns
    -------
    PredictResponse
        Column-dict tables plus ``model`` and ``request_id``.

    Raises
    ------
    HTTPException
        Status 400 when coerce or predict fails. FoMo has no custom
        exception types. FastAPI/Pydantic body validation on this
        JSON route is 422, not 400.

    See Also
    --------
    PredictRequest
        JSON body schema.
    fomo.types.converters.coerce_request
        Wire conversion to ``CoercedPredictRequest``.
    predict_bytes
        Multipart / Arrow envelope variant.
    """
    request_id = str(uuid.uuid4())

    try:
        coerced = coerce_request(request)
        response = http_request.app.state.runtime.scheduler.run(coerced)

    # An HTTPException already carries a chosen status and detail; re-wrapping
    # it would force it to 400 and flatten the detail into a stringified dict.
    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "code": "request_failed",
                "request_id": request_id,
            },
        ) from exc

    return PredictResponse(
        predictions=response.predictions.to_dict(as_series=False),
        model=response.model,
        request_id=request_id,
        quantiles=(
            response.quantiles.to_dict(as_series=False)
            if response.quantiles is not None
            else None
        ),
    )


@router.post("/predict/bytes")
async def predict_bytes(
    http_request: Request,
    metadata: Annotated[str, Form()],
    past: Annotated[UploadFile, File()],
    future: Annotated[UploadFile | None, File()] = None,
    static: Annotated[UploadFile | None, File()] = None,
) -> Response:
    """Run a multipart ``POST /predict/bytes``.

    Form field ``metadata`` is a JSON string; file ``past`` is
    required; ``future`` and ``static`` are optional. Empty file bodies
    for ``future``/``static`` are skipped (not attached). ``past`` is
    always included.

    After ``json.loads(metadata)``, calls ``decode_request``, then
    ``scheduler.run``. Sets ``response.request_id`` to a UUID (sktime
    ``to_response`` leaves ``""``), then ``encode_response`` and
    ``pack_envelope``. Media type is
    ``application/vnd.fomo.predict+arrow``. Failures use the same
    HTTP 400 wrapping as ``predict``.

    Parameters
    ----------
    http_request : fastapi.Request
        Used to read ``app.state.runtime.scheduler``.
    metadata : str
        JSON object of scalar predict fields (multipart ``metadata``).
    past : fastapi.UploadFile
        Required past-frame bytes.
    future : fastapi.UploadFile, optional
        Optional future-frame bytes; omitted when the body is empty.
    static : fastapi.UploadFile, optional
        Optional static-frame bytes; omitted when the body is empty.

    Returns
    -------
    fastapi.Response
        Packed ``FOMO`` envelope with media type
        ``application/vnd.fomo.predict+arrow``.

    Raises
    ------
    HTTPException
        Status 400 when JSON parse, decode, or predict fails.

    See Also
    --------
    PredictRequest
        Field semantics split across metadata vs files.
    fomo.types.converters.decode_request
        Rebuilds ``CoercedPredictRequest`` from metadata + Arrow.
    fomo.types.converters.encode_response
        Splits the coerced response into metadata and files.
    fomo.types.converters.pack_envelope
        Binary envelope written as the response body.
    predict
        JSON variant that assigns ``request_id`` on ``PredictResponse``.
    """
    files = {"past": await past.read()}
    if future is not None:
        blob = await future.read()
        if blob:
            files["future"] = blob
    if static is not None:
        blob = await static.read()
        if blob:
            files["static"] = blob

    request_id = str(uuid.uuid4())

    try:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError as error:
            raise ValueError(
                "the multipart 'metadata' field is not valid JSON.\n\nOriginal error: "
                f"{error}\n\nSend it as a JSON object of the non-frame predict fields, "
                'e.g. metadata={{"fh": 3, "model": "naive"}}. The frames themselves go '
                "in the separate 'past' / 'future' / 'static' file parts."
            ) from error

        request = decode_request(parsed_metadata, files)
        response = http_request.app.state.runtime.scheduler.run(request)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "code": "request_failed",
                "request_id": request_id,
            },
        ) from exc

    response.request_id = request_id

    response_metadata, response_files = encode_response(response)
    return Response(
        content=pack_envelope(response_metadata, response_files),
        media_type=_ENVELOPE_CONTENT_TYPE,
    )
