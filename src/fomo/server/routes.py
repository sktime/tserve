"""HTTP routes for health, listing, stats, and forecast.

Mounted on the FastAPI app by ``Server``. Forecast handlers use *wire*
converters in ``fomo.types.converters`` (``coerce_request``,
``decode_request``, ``encode_response``, ``pack_envelope``), not the
sktime *convertors* in ``fomo.runtime.executors.sktime.convertors``.

``request.model`` is a loaded model id. ``request_id`` is assigned in
these handlers: the JSON path puts a UUID on ``ForecastResponse``
directly; the bytes path overwrites
``CoercedForecastResponse.request_id`` after predict (sktime
``to_response`` sets ``""``). FoMo has no custom exception types;
forecast failures become ``HTTPException`` 400.
"""

import json
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile

from fomo.types import (
    ForecastRequest,
    ForecastResponse,
    HealthResult,
    ModelsResult,
    StatsResult,
)
from fomo.types.converters import (
    coerce_request,
    decode_request,
    encode_response,
    pack_envelope,
)

_ENVELOPE_CONTENT_TYPE = "application/vnd.fomo.forecast+arrow"
"""Media type for ``POST /forecast/bytes`` envelope bodies."""


router = APIRouter()
"""FastAPI router included by ``Server`` (health, models, stats, forecast)."""


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


@router.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest, http_request: Request) -> ForecastResponse:
    """Run a JSON ``POST /forecast``.

    Assigns a UUID ``request_id``, coerces the body with
    ``coerce_request``, then ``scheduler.run``. On success, returns
    ``ForecastResponse`` with ``predictions`` (and ``quantiles`` when
    present) as ``to_dict(as_series=False)``, ``model`` from the
    executor response, and the UUID. Handler failures (coerce or
    predict) become ``HTTPException`` 400 with ``detail``
    ``{error: str(exc), code: "request_failed", request_id}``. Invalid
    JSON bodies that fail ``ForecastRequest`` validation are rejected
    by FastAPI as 422 before this handler runs.

    ``request.model`` is a loaded model id, not an executor name.
    ``context``, ``freq``, and ``params`` are accepted on
    ``ForecastRequest`` but unused by current executors; ``series_id``
    is rejected by the sktime convertor.

    Parameters
    ----------
    request : ForecastRequest
        JSON body. See that class for fields.
    http_request : fastapi.Request
        Used to read ``app.state.runtime.scheduler``.

    Returns
    -------
    ForecastResponse
        Column-dict tables plus ``model`` and ``request_id``.

    Raises
    ------
    HTTPException
        Status 400 when coerce or predict fails. FoMo has no custom
        exception types. FastAPI/Pydantic body validation on this
        JSON route is 422, not 400.

    See Also
    --------
    ForecastRequest
        JSON body schema.
    fomo.types.converters.coerce_request
        Wire conversion to ``CoercedForecastRequest``.
    forecast_bytes
        Multipart / Arrow envelope variant.
    """
    request_id = str(uuid.uuid4())

    try:
        coerced = coerce_request(request)
        response = http_request.app.state.runtime.scheduler.run(coerced)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": str(exc), "code": "request_failed", "request_id": request_id},
        ) from exc

    return ForecastResponse(
        predictions=response.predictions.to_dict(as_series=False),
        model=response.model,
        request_id=request_id,
        quantiles=(
            response.quantiles.to_dict(as_series=False)
            if response.quantiles is not None
            else None
        ),
    )


@router.post("/forecast/bytes")
async def forecast_bytes(
    http_request: Request,
    metadata: str = Form(),
    history: UploadFile = File(),
    future: UploadFile | None = File(None),
    static: UploadFile | None = File(None),
) -> Response:
    """Run a multipart ``POST /forecast/bytes``.

    Form field ``metadata`` is a JSON string; file ``history`` is
    required; ``future`` and ``static`` are optional. Empty file bodies
    for ``future``/``static`` are skipped (not attached). ``history`` is
    always included.

    After ``json.loads(metadata)``, calls ``decode_request``, then
    ``scheduler.run``. Sets ``response.request_id`` to a UUID (sktime
    ``to_response`` leaves ``""``), then ``encode_response`` and
    ``pack_envelope``. Media type is
    ``application/vnd.fomo.forecast+arrow``. Failures use the same
    HTTP 400 wrapping as ``forecast``.

    Parameters
    ----------
    http_request : fastapi.Request
        Used to read ``app.state.runtime.scheduler``.
    metadata : str
        JSON object of scalar forecast fields (multipart ``metadata``).
    history : fastapi.UploadFile
        Required history-frame bytes.
    future : fastapi.UploadFile, optional
        Optional future-frame bytes; omitted when the body is empty.
    static : fastapi.UploadFile, optional
        Optional static-frame bytes; omitted when the body is empty.

    Returns
    -------
    fastapi.Response
        Packed ``FOMO`` envelope with media type
        ``application/vnd.fomo.forecast+arrow``.

    Raises
    ------
    HTTPException
        Status 400 when JSON parse, decode, or predict fails.

    See Also
    --------
    ForecastRequest
        Field semantics split across metadata vs files.
    fomo.types.converters.decode_request
        Rebuilds ``CoercedForecastRequest`` from metadata + Arrow.
    fomo.types.converters.encode_response
        Splits the coerced response into metadata and files.
    fomo.types.converters.pack_envelope
        Binary envelope written as the response body.
    forecast
        JSON variant that assigns ``request_id`` on ``ForecastResponse``.
    """
    files = {"history": await history.read()}
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
        metadata = json.loads(metadata)
        request = decode_request(metadata, files)
        response = http_request.app.state.runtime.scheduler.run(request)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": str(exc), "code": "request_failed", "request_id": request_id},
        ) from exc

    response.request_id = request_id

    metadata, files = encode_response(response)
    return Response(
        content=pack_envelope(metadata, files),
        media_type=_ENVELOPE_CONTENT_TYPE,
    )
