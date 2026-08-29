import narwhals as nw
import pytest

from fomo.types.converters import (
    coerce_request,
    coerce_response,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    pack_envelope,
    unpack_envelope,
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


@pytest.mark.parametrize(
    "history",
    [
        pytest.param(
            {
                "timestamp": ["2024-01-01"],
                "sales": [120],
            },
            id="column_dict",
        ),
        pytest.param(
            {
                "columns": ["timestamp", "sales"],
                "data": [
                    ["2024-01-01", 120],
                ],
            },
            id="columns_data",
        ),
    ],
)
def test_coerce_request(history):
    request = _request(history=history)
    original_history = request.history

    coerced = coerce_request(request)

    assert isinstance(coerced, CoercedForecastRequest)
    assert isinstance(coerced.history, nw.DataFrame)
    assert coerced.future is None
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

    assert isinstance(decoded, CoercedForecastRequest)
    assert isinstance(decoded.history, nw.DataFrame)
    assert decoded.future is None
    assert decoded.model == "naive"


def test_coerce_response():
    response = _response(
        quantiles={"timestamp": ["2024-01-02"], "sales_0.5": [120.0]},
    )
    original_predictions = response.predictions

    coerced = coerce_response(response)

    assert isinstance(coerced, CoercedForecastResponse)
    assert isinstance(coerced.predictions, nw.DataFrame)
    assert isinstance(coerced.quantiles, nw.DataFrame)
    assert response.predictions is original_predictions


def test_encode_response():
    metadata, files = encode_response(coerce_response(_response()))

    assert "predictions" in files
    assert "quantiles" not in files
    assert metadata["model"] == "naive"
    assert "predictions" not in metadata


def test_decode_response():
    decoded = decode_response(*encode_response(coerce_response(_response())))

    assert isinstance(decoded, CoercedForecastResponse)
    assert isinstance(decoded.predictions, nw.DataFrame)
    assert decoded.quantiles is None
    assert decoded.request_id == "req-1"


def test_pack_envelope():
    metadata, files = encode_response(coerce_response(_response()))

    body = pack_envelope(metadata, files)

    assert body[:4] == b"FOMO"
    assert body[4] == 1


def test_unpack_envelope():
    metadata, files = encode_response(coerce_response(_response()))

    got_metadata, got_files = unpack_envelope(pack_envelope(metadata, files))

    assert got_metadata["model"] == "naive"
    assert got_metadata["request_id"] == "req-1"
    assert set(got_files) == {"predictions"}


@pytest.mark.parametrize(
    ("body", "match"),
    [
        pytest.param(b"short", "invalid forecast envelope: truncated", id="too_short"),
        pytest.param(
            b"XXXX\x01\x00\x00\x00\x00",
            "invalid forecast envelope: expected FOMO magic bytes",
            id="bad_magic",
        ),
        pytest.param(
            b"FOMO\x02\x00\x00\x00\x00",
            "invalid forecast envelope: unsupported version 2",
            id="bad_version",
        ),
    ],
)
def test_unpack_envelope_rejects(body, match):
    with pytest.raises(ValueError, match=match):
        unpack_envelope(body)
