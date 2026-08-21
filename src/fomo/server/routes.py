import json
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile

from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult
from fomo.types.converters import coerce_request, decode_request, encode_response

router = APIRouter()


@router.get("/health", response_model=HealthResult, response_model_exclude_none=True)
def health() -> HealthResult:
    return HealthResult(status="ok")


@router.get("/models", response_model=ModelsResult)
def models(request: Request) -> ModelsResult:
    return request.app.state.runtime.loaded_models()


@router.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest, http_request: Request) -> ForecastResponse:
    request_id = str(uuid.uuid4())

    try:
        request = coerce_request(request)
        response = http_request.app.state.runtime.scheduler.run(request)

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
    response.predictions = response.predictions.to_dict(as_series=False)
    if response.quantiles is not None:
        response.quantiles = response.quantiles.to_dict(as_series=False)

    return response


@router.post("/forecast/bytes")
async def forecast_bytes(
    http_request: Request,
    metadata: str = Form(),
    history: UploadFile = File(),
    future: UploadFile | None = File(None),
    static: UploadFile | None = File(None),
) -> Response:
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
        request: ForecastRequest = decode_request(metadata, files)
        response = http_request.app.state.runtime.scheduler.run(request)

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

    metadata, files = encode_response(response)
    boundary = uuid.uuid4().hex
    body = bytearray()

    def add(name: str, content: bytes) -> None:
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode())
        body.extend(content)
        body.extend(b"\r\n")

    add("response", json.dumps(metadata).encode())
    for name, blob in files.items():
        add(name, blob)
    body.extend(f"--{boundary}--\r\n".encode())

    return Response(
        content=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
