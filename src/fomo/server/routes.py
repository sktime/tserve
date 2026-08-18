import uuid

from fastapi import APIRouter, HTTPException, Request

from fomo.errors import error_payload
from fomo.runtime.adapt import job_from_request, result_to_response
from fomo.runtime.registry import MODELS
from fomo.types import ForecastRequest, ForecastResult, HealthResult, ModelsResult

router = APIRouter()


@router.get("/health", response_model=HealthResult, response_model_exclude_none=True)
def health() -> HealthResult:
    return HealthResult(status="ok")


@router.get("/models", response_model=ModelsResult)
def models() -> ModelsResult:
    return MODELS


@router.post("/forecast", response_model=ForecastResult)
def forecast(request_body: ForecastRequest, request: Request) -> ForecastResult:
    request_id = str(uuid.uuid4())
    try:
        job = job_from_request(request_body)
        result = request.app.state.runtime.scheduler.run(job)
        response = result_to_response(result)
    except Exception as exc:
        status_code, detail = error_payload(exc, request_id)
        raise HTTPException(status_code=status_code, detail=detail) from exc
    response.request_id = request_id
    return response
