import uuid

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import ValidationError

from fomo.runtime.registry import loaded_models
from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult
from fomo.types.codec import (
    ARROW_CONTENT_TYPE,
    decode_forecast_arrow,
    encode_forecast_response_arrow,
)
from fomo.types.converters import request_to_frames, response_to_tables

router = APIRouter()


@router.get("/health", response_model=HealthResult, response_model_exclude_none=True)
def health() -> HealthResult:
    return HealthResult(status="ok")


@router.get("/models", response_model=ModelsResult)
def models(request: Request) -> ModelsResult:
    return loaded_models(request.app.state.runtime.models)


def _content_type(request: Request) -> str:
    return (request.headers.get("content-type") or "").split(";", 1)[0].strip().lower()


def _run_forecast(
    request_body: ForecastRequest,
    request: Request,
    *,
    frames: bool,
) -> ForecastResponse:
    request_id = str(uuid.uuid4())
    try:
        request_body = request_to_frames(request_body)
        response = request.app.state.runtime.scheduler.run(request_body)
        if not frames:
            response = response_to_tables(response)
    except Exception as exc:
        if isinstance(exc, ValueError):
            status_code, code = 400, "bad_request"
        elif isinstance(exc, RuntimeError):
            status_code, code = 503, "model_unavailable"
        else:
            status_code, code = 500, "internal_error"
        raise HTTPException(
            status_code=status_code,
            detail={"error": str(exc), "code": code, "request_id": request_id},
        ) from exc
    response.request_id = request_id
    return response


@router.post("/forecast", response_model=None)
async def forecast(request: Request) -> ForecastResponse | Response:
    if _content_type(request) == ARROW_CONTENT_TYPE:
        try:
            request_body = decode_forecast_arrow(await request.body())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        response = _run_forecast(request_body, request, frames=True)
        return Response(
            content=encode_forecast_response_arrow(response),
            media_type=ARROW_CONTENT_TYPE,
        )

    try:
        request_body = ForecastRequest.model_validate(await request.json())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return _run_forecast(request_body, request, frames=False)
