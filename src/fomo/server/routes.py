import uuid

from fastapi import APIRouter, HTTPException, Request

from fomo.runtime.adapt import job_from_request, result_to_response
from fomo.runtime.registry import MODELS
from fomo.server.schemas import (
    ErrorResponse,
    ForecastRequest,
    ForecastResponse,
    ModelInfo,
    ModelsResponse,
)

router = APIRouter()


def error_response(*, status_code: int, code: str, message: str, request_id: str, details=None):
    return HTTPException(
        status_code=status_code,
        detail=ErrorResponse(
            error=message,
            code=code,
            request_id=request_id,
            details=details,
        ).model_dump(),
    )


@router.get("/health")
def health(request: Request) -> dict:
    return request.app.state.runtime.health()


@router.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    return ModelsResponse(
        models=[
            ModelInfo(
                alias=spec.alias,
                estimator=spec.estimator,
                executor=spec.executor,
                multivariate=spec.multivariate,
                exogenous=spec.exogenous,
                quantiles=spec.quantiles,
            )
            for spec in MODELS.values()
        ]
    )


@router.post("/forecast", response_model=ForecastResponse)
def forecast(request_body: ForecastRequest, request: Request) -> ForecastResponse:
    request_id = str(uuid.uuid4())
    try:
        job = job_from_request(request_body)
        result = request.app.state.runtime.scheduler.run(job)
        response = result_to_response(result)
    except ValueError as exc:
        raise error_response(
            status_code=400,
            code="bad_request",
            message=str(exc),
            request_id=request_id,
        ) from exc
    except RuntimeError as exc:
        raise error_response(
            status_code=503,
            code="model_unavailable",
            message=str(exc),
            request_id=request_id,
        ) from exc
    except Exception as exc:
        raise error_response(
            status_code=500,
            code="internal_error",
            message=str(exc),
            request_id=request_id,
        ) from exc
    response.request_id = request_id
    return response
