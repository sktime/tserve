import narwhals as nw
import pytest

from tserve.types.converters import (
    _from_arrow_bytes,
    _from_narwhals,
    _to_bytes,
    _to_narwhals,
    coerce_request,
    coerce_response,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    pack_envelope,
    unpack_envelope,
)
from tserve.types.models import (
    CoercedPredictRequest,
    CoercedPredictResponse,
    PredictRequest,
    PredictResponse,
)


def _request(**kwargs):
    payload = {
        "past": {"timestamp": ["2024-01-01"], "sales": [120]},
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return PredictRequest.model_validate(payload)


def _response(**kwargs):
    payload = {
        "predictions": {"timestamp": ["2024-01-02"], "sales": [120.0]},
        "model": "naive",
        "request_id": "req-1",
    }
    payload.update(kwargs)
    return PredictResponse.model_validate(payload)


@pytest.mark.parametrize(
    "past",
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
def test_coerce_request(past):
    request = _request(past=past)
    original_past = request.past

    coerced = coerce_request(request)

    assert isinstance(coerced, CoercedPredictRequest)
    assert isinstance(coerced.past, nw.DataFrame)
    assert coerced.future is None
    assert coerced.static is None
    assert request.past is original_past


def test_coerce_request_omitted_time_uses_first_past_column():
    request = _request(time=None)

    coerced = coerce_request(request)

    assert request.time is None
    assert coerced.time == "timestamp"


def test_coerce_request_target_str_becomes_one_element_list():
    request = _request(target="sales")

    coerced = coerce_request(request)

    assert request.target == "sales"
    assert coerced.target == ["sales"]


def test_coerce_request_omitted_target_infers_non_time_non_future_columns():
    request = _request(
        past={
            "timestamp": ["2024-01-01"],
            "sales": [120],
            "price": [9.99],
        },
        time=None,
        target=None,
        future={"timestamp": ["2024-01-02"], "price": [8.99]},
    )

    coerced = coerce_request(request)

    assert request.target is None
    assert coerced.time == "timestamp"
    assert coerced.target == ["sales"]


def test_coerce_request_omitted_target_without_future_excludes_only_time():
    request = _request(
        past={"timestamp": ["2024-01-01"], "sales": [120], "promo": [0]},
        target=None,
    )

    coerced = coerce_request(request)

    assert coerced.target == ["sales", "promo"]


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            {
                "past": {"timestamp": ["2024-01-01", "2024-01-02"]},
                "target": None,
            },
            id="time_only_past",
        ),
        pytest.param(
            {
                "past": {"timestamp": ["2024-01-01"], "sales": [120]},
                "future": {"sales": [1]},
                "target": None,
            },
            id="future_holds_value_column",
        ),
    ],
)
def test_coerce_request_rejects_empty_inferred_target(kwargs):
    with pytest.raises(ValueError, match="could not infer a target column"):
        coerce_request(_request(**kwargs))


def test_coerce_request_rejects_pandas_index_as_time():
    pd = pytest.importorskip("pandas")
    past = pd.DataFrame(
        {"sales": [1, 2, 3]},
        index=pd.date_range("2024-01-01", periods=3, freq="D"),
    )

    with pytest.raises(ValueError, match="reset_index"):
        coerce_request(_request(past=past, time=None, target=None))


@pytest.mark.parametrize(
    ("df", "error", "match"),
    [
        pytest.param(
            None,
            TypeError,
            "is not a table TServe can read",
            id="none",
        ),
        pytest.param(
            {"timestamp": ["2024-01-01", "2024-01-02"], "sales": [1, "2"]},
            ValueError,
            "could not convert to a single Arrow type",
            id="mixed_types",
        ),
        pytest.param(
            {"timestamp": ["2024-01-01", "2024-01-02"], "sales": [{"x": 1}, 2]},
            ValueError,
            "could not convert to a single Arrow type",
            id="nested_object",
        ),
    ],
)
def test_to_narwhals_rejects(df, error, match):
    with pytest.raises(error, match=match):
        _to_narwhals(df, name="past")


def test_encode_request():
    metadata, files = encode_request(coerce_request(_request()))

    assert "past" in files
    assert "future" not in files
    assert "static" not in files
    assert metadata["time"] == "timestamp"
    assert "past" not in metadata


def test_decode_request():
    decoded = decode_request(*encode_request(coerce_request(_request())))

    assert isinstance(decoded, CoercedPredictRequest)
    assert isinstance(decoded.past, nw.DataFrame)
    assert decoded.future is None
    assert decoded.model == "naive"


def test_coerce_response():
    response = _response(
        quantiles={"timestamp": ["2024-01-02"], "sales_0.5": [120.0]},
    )
    original_predictions = response.predictions

    coerced = coerce_response(response)

    assert isinstance(coerced, CoercedPredictResponse)
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

    assert isinstance(decoded, CoercedPredictResponse)
    assert isinstance(decoded.predictions, nw.DataFrame)
    assert decoded.quantiles is None
    assert decoded.request_id == "req-1"


def test_pack_envelope():
    metadata, files = encode_response(coerce_response(_response()))

    body = pack_envelope(metadata, files)

    assert body[:4] == b"TSRV"
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
        pytest.param(b"short", "invalid predict envelope: truncated", id="too_short"),
        pytest.param(
            b"XXXX\x01\x00\x00\x00\x00",
            "invalid predict envelope: expected TSRV magic bytes",
            id="bad_magic",
        ),
        pytest.param(
            b"TSRV\x02\x00\x00\x00\x00",
            "invalid predict envelope: unsupported version 2",
            id="bad_version",
        ),
    ],
)
def test_unpack_envelope_rejects(body, match):
    with pytest.raises(ValueError, match=match):
        unpack_envelope(body)


def test_from_arrow_bytes_roundtrip():
    frame = _to_narwhals({"timestamp": ["2024-01-01"], "sales": [120]})

    out = _from_arrow_bytes(_to_bytes(frame), name="past")

    assert list(out.columns) == ["timestamp", "sales"]
    assert out["sales"].to_list() == [120]


@pytest.mark.parametrize(
    "blob",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b"not-arrow", id="text"),
        pytest.param(b"\x00\x01\x02\x03\x04\x05\x06\x07", id="garbage"),
    ],
)
def test_from_arrow_bytes_rejects(blob):
    with pytest.raises(ValueError, match="could not be read as an Arrow IPC stream"):
        _from_arrow_bytes(blob, name="past")


_TEMPLATE_COLUMNS = {"timestamp": ["2024-01-01"], "sales": [120.0]}


def _column_dict_template():
    return {"timestamp": ["2024-01-01"], "sales": [120]}


def _columns_data_template():
    return {
        "columns": ["timestamp", "sales"],
        "data": [["2024-01-01", 120]],
    }


def _pyarrow_template():
    pa = pytest.importorskip("pyarrow")
    return pa.table(_TEMPLATE_COLUMNS)


def _narwhals_pyarrow_template():
    return nw.from_dict(_TEMPLATE_COLUMNS, backend="pyarrow")


def _narwhals_pandas_template():
    pd = pytest.importorskip("pandas")
    return nw.from_native(pd.DataFrame(_TEMPLATE_COLUMNS))


def _pandas_template():
    pd = pytest.importorskip("pandas")
    return pd.DataFrame(_TEMPLATE_COLUMNS)


def _polars_template():
    pl = pytest.importorskip("polars")
    return pl.DataFrame(_TEMPLATE_COLUMNS)


@pytest.mark.parametrize(
    "make_template",
    [
        pytest.param(_column_dict_template, id="column_dict"),
        pytest.param(_columns_data_template, id="columns_data"),
        pytest.param(_pyarrow_template, id="pyarrow"),
        pytest.param(_narwhals_pyarrow_template, id="narwhals_pyarrow"),
        pytest.param(_narwhals_pandas_template, id="narwhals_pandas"),
        pytest.param(_pandas_template, id="pandas"),
        pytest.param(_polars_template, id="polars"),
    ],
)
def test_from_narwhals(make_template):
    template = make_template()
    out = _from_narwhals(
        _to_narwhals({"timestamp": ["2024-01-02"], "sales": [120.0]}),
        template,
    )

    if isinstance(template, dict):
        assert type(out) is dict
        if set(template) == {"columns", "data"}:
            assert set(out) == {"columns", "data"}
            assert out["columns"] == template["columns"]
        else:
            assert set(out) == set(template)
            assert "columns" not in out
        return

    if isinstance(template, nw.DataFrame):
        assert isinstance(out, nw.DataFrame)
        assert out.implementation == template.implementation
        assert list(out.columns) == list(template.columns)
        return

    assert type(out) is type(template)
    columns = getattr(out, "column_names", None) or list(out.columns)
    assert list(columns) == ["timestamp", "sales"]
