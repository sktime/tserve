"""Arrow IPC wire codec for Narwhals forecast tables."""

from __future__ import annotations

import json
import struct
import narwhals as nw
import pyarrow as pa

from fomo.types.models import ForecastRequest, ForecastResponse

ARROW_CONTENT_TYPE = "application/vnd.fomo.forecast+arrow"
_MAGIC = b"FOMOA1\n"
_U32 = struct.Struct(">I")

_META_KEYS = (
    "time",
    "target",
    "horizon",
    "model",
    "series_id",
    "known_future",
    "past_only",
    "freq",
    "quantiles",
    "params",
)


def _require_frame(value: object, field: str) -> nw.DataFrame:
    if not isinstance(value, nw.DataFrame):
        raise TypeError(f"{field} must be a Narwhals DataFrame for Arrow transport")
    return value


def frame_to_ipc(frame: nw.DataFrame) -> bytes:
    table = frame.to_arrow()
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


def ipc_to_frame(data: bytes) -> nw.DataFrame:
    with pa.ipc.open_stream(data) as reader:
        return nw.from_arrow(reader.read_all(), backend="pandas")


def _encode(meta: dict[str, object], tables: tuple[tuple[str, object], ...]) -> bytes:
    meta_bytes = json.dumps(meta, separators=(",", ":"), default=str).encode("utf-8")
    parts = [_MAGIC, _U32.pack(len(meta_bytes)), meta_bytes]
    for field, value in tables:
        if value is None:
            parts.append(_U32.pack(0))
            continue
        blob = frame_to_ipc(_require_frame(value, field))
        parts.append(_U32.pack(len(blob)))
        parts.append(blob)
    return b"".join(parts)


def _decode(body: bytes, fields: tuple[str, ...]) -> tuple[dict[str, object], dict[str, nw.DataFrame | None]]:
    if not body.startswith(_MAGIC):
        raise ValueError("invalid FOMO Arrow payload: bad magic")
    offset = len(_MAGIC)

    def read_chunk() -> bytes:
        nonlocal offset
        if offset + 4 > len(body):
            raise ValueError("invalid FOMO Arrow payload: truncated length")
        (length,) = _U32.unpack_from(body, offset)
        offset += 4
        end = offset + length
        if end > len(body):
            raise ValueError("invalid FOMO Arrow payload: truncated chunk")
        chunk = body[offset:end]
        offset = end
        return chunk

    meta: dict[str, object] = json.loads(read_chunk().decode("utf-8"))
    tables = {}
    for field in fields:
        blob = read_chunk()
        tables[field] = ipc_to_frame(blob) if blob else None
    if offset != len(body):
        raise ValueError("invalid FOMO Arrow payload: trailing data")
    return meta, tables


def encode_forecast_arrow(request: ForecastRequest) -> bytes:
    meta = {key: getattr(request, key) for key in _META_KEYS}
    meta = {key: value for key, value in meta.items() if value is not None}
    return _encode(
        meta,
        (
            ("history", request.history),
            ("future", request.future),
            ("static", request.static),
        ),
    )


def decode_forecast_arrow(body: bytes) -> ForecastRequest:
    meta, tables = _decode(body, ("history", "future", "static"))
    if tables["history"] is None:
        raise ValueError("history table is required in Arrow payload")
    return ForecastRequest(
        history=tables["history"],
        future=tables["future"],
        static=tables["static"],
        **meta,
    )


def encode_forecast_response_arrow(response: ForecastResponse) -> bytes:
    meta = {
        "model": response.model,
        "request_id": response.request_id,
    }
    return _encode(
        meta,
        (
            ("predictions", response.predictions),
            ("quantiles", response.quantiles),
        ),
    )


def decode_forecast_response_arrow(body: bytes) -> ForecastResponse:
    meta, tables = _decode(body, ("predictions", "quantiles"))
    if tables["predictions"] is None:
        raise ValueError("predictions table is required in Arrow payload")
    return ForecastResponse(
        predictions=tables["predictions"],
        quantiles=tables["quantiles"],
        **meta,
    )
