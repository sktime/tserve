import narwhals as nw
import narwhals.testing as nwt
import pyarrow as pa
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

    assert isinstance(coerced, CoercedForecastRequest)
    assert isinstance(coerced.history, nw.DataFrame)
    assert isinstance(coerced.future, nw.DataFrame)
    assert coerced.static is None
    assert request.history is original_history

def test_coerce_request_columns_data():
    hist_dict = {
              "columns": ["timestamp", "sales"],
              "data": [
                ["2024-01-01", 120],
                ["2024-01-02", 135],
                ["2024-01-03", 128],
                ["2024-01-04", 142],
                ["2024-01-05", 138]
              ]
            }

    request = _request(history=hist_dict)
    coerced_request = coerce_request(request)
    expected_table = pa.Table.from_arrays([[k[0] for k in hist_dict["data"]],
                                           [k[1] for k in hist_dict["data"]]], names=hist_dict["columns"])
    nw_df = nw.from_native(expected_table)
    nwt.assert_frame_equal(nw_df, coerced_request.history)


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
        pytest.param(b"short", "invalid forecast envelope", id="too_short"),
        pytest.param(b"XXXX\x01\x00\x00\x00\x00", "invalid forecast envelope", id="bad_magic"),
        pytest.param(b"FOMO\x02\x00\x00\x00\x00", "invalid forecast envelope", id="bad_version"),
    ],
)
def test_unpack_envelope_rejects(body, match):
    with pytest.raises(ValueError, match=match):
        unpack_envelope(body)
