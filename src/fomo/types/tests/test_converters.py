import narwhals as nw

from fomo.types.converters import (
    coerce_request,
    coerce_response,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
)
from fomo.types.models import (
    CoercedForecastRequest,
    CoercedForecastResponse,
    ForecastRequest,
    ForecastResponse,
)


def _request(**kwargs):
    payload = {
        "history": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "horizon": 1,
        "context": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return ForecastRequest.model_validate(payload)


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return ForecastResponse.model_validate(payload)


def test_coerce_request():
    request = _request(
        future={"timestamp": ["2024-01-02"], "price": [8.99]},
        known_future=["price"],
        history={"timestamp": ["2024-01-01"], "sales": [120], "price": [9.99]},
    )
    original_history = request.history

    coerced = coerce_request(request)

    assert type(coerced) is CoercedForecastRequest
    assert type(coerced.history) is nw.DataFrame
    assert type(coerced.future) is nw.DataFrame
    assert coerced.static is None
    assert request.history is original_history


def test_encode_request():
    metadata, files = encode_request(coerce_request(_request()))

    assert "history" in files
    assert "future" not in files
    assert "static" not in files
    assert metadata["time"] == "timestamp"
    assert "history" not in metadata


def test_decode_request():
    decoded = decode_request(*encode_request(coerce_request(_request())))

    assert type(decoded) is CoercedForecastRequest
    assert type(decoded.history) is nw.DataFrame
    assert decoded.future is None
    assert decoded.model == "naive"


def test_coerce_response():
    response = _response(
        quantiles={"timestamp": ["2024-01-02"], "sales_0.5": [120.0]},
    )
    original_predictions = response.predictions

    coerced = coerce_response(response)

    assert type(coerced) is CoercedForecastResponse
    assert type(coerced.predictions) is nw.DataFrame
    assert type(coerced.quantiles) is nw.DataFrame
    assert response.predictions is original_predictions


def test_encode_response():
    metadata, files = encode_response(coerce_response(_response()))

    assert "predictions" in files
    assert "quantiles" not in files
    assert metadata["model"] == "naive"
    assert "predictions" not in metadata


def test_decode_response():
    decoded = decode_response(*encode_response(coerce_response(_response())))

    assert type(decoded) is CoercedForecastResponse
    assert type(decoded.predictions) is nw.DataFrame
    assert decoded.quantiles is None
    assert decoded.request_id == "req-1"
