import io
import json
import struct
from typing import Any

import narwhals as nw
import pandas as pd
import pyarrow as pa
from narwhals.typing import IntoFrame

from fomo.types.models import (
    CoercedForecastRequest,
    CoercedForecastResponse,
    ForecastRequest,
    ForecastResponse,
)


def _to_narwhals(df: IntoFrame | dict[str, list]) -> nw.DataFrame:
    if type(df) == nw.DataFrame:
        return df
    if type(df) == dict:
        return nw.from_dict(df, backend="pyarrow")
    return nw.from_native(df, eager_only=True)


def _to_bytes(df: nw.DataFrame) -> bytes:
    df = df.to_arrow()
    sink = io.BytesIO()
    with pa.ipc.new_stream(sink, df.schema) as writer:
        writer.write_table(df)
    return sink.getvalue()


def coerce_request(request: ForecastRequest) -> CoercedForecastRequest:
    payload = request.model_dump(exclude={"history", "future", "static"})
    payload["history"] = _to_narwhals(request.history)
    payload["future"] = _to_narwhals(request.future) if request.future is not None else None
    payload["static"] = _to_narwhals(request.static) if request.static is not None else None

    return CoercedForecastRequest.model_validate(payload)


def encode_request(request: CoercedForecastRequest) -> tuple[dict, dict[str, bytes]]:
    bytes_encoded = {}
    for frame in ['history', 'future', 'static']:
        value = getattr(request, frame)
        if value is not None:
            bytes_encoded[frame] = _to_bytes(value)

    metadata = request.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_request(metadata: dict, bytes_encoded: dict[str, bytes]) -> CoercedForecastRequest:
    payload = dict(metadata)
    for frame in ['history', 'future', 'static']:
        if frame in bytes_encoded:
            payload[frame] = nw.from_arrow(pa.ipc.open_stream(io.BytesIO(bytes_encoded[frame])).read_all(), backend="pyarrow")
    return CoercedForecastRequest.model_validate(payload)


def coerce_response(response: ForecastResponse) -> CoercedForecastResponse:
    payload = response.model_dump(exclude={"predictions", "quantiles"})
    payload["predictions"] = _to_narwhals(response.predictions)
    payload["quantiles"] = (
        _to_narwhals(response.quantiles) if response.quantiles is not None else None
    )
    return CoercedForecastResponse.model_validate(payload)


def encode_response(response: CoercedForecastResponse) -> tuple[dict, dict[str, bytes]]:
    bytes_encoded = {}
    for frame in ['predictions', 'quantiles']:
        value = getattr(response, frame)
        if value is not None:
            bytes_encoded[frame] = _to_bytes(value)

    metadata = response.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_response(metadata: dict, bytes_encoded: dict[str, bytes]) -> CoercedForecastResponse:
    payload = dict(metadata)
    for frame in ['predictions', 'quantiles']:
        if frame in bytes_encoded:
            payload[frame] = nw.from_arrow(pa.ipc.open_stream(io.BytesIO(bytes_encoded[frame])).read_all(), backend="pyarrow")
    return CoercedForecastResponse.model_validate(payload)


def pack_envelope(metadata: dict, files: dict[str, bytes]) -> bytes:
    parts = [("response", json.dumps(metadata).encode()), *files.items()]
    body = bytearray(b"FOMO")
    body.append(1)
    body.extend(struct.pack("<I", len(parts)))
    for name, payload in parts:
        name_b = name.encode()
        body.extend(struct.pack("<I", len(name_b)))
        body.extend(name_b)
        body.extend(struct.pack("<I", len(payload)))
        body.extend(payload)
    return bytes(body)


def unpack_envelope(body: bytes) -> tuple[dict, dict[str, bytes]]:
    if len(body) < 9 or body[:4] != b"FOMO" or body[4] != 1:
        raise ValueError("invalid forecast envelope")
    n_parts = struct.unpack_from("<I", body, 5)[0]
    offset = 9
    metadata: dict = {}
    files: dict[str, bytes] = {}
    for _ in range(n_parts):
        if offset + 4 > len(body):
            raise ValueError("invalid forecast envelope")
        name_len = struct.unpack_from("<I", body, offset)[0]
        offset += 4
        name = body[offset : offset + name_len].decode()
        offset += name_len
        payload_len = struct.unpack_from("<I", body, offset)[0]
        offset += 4
        payload = bytes(body[offset : offset + payload_len])
        offset += payload_len
        if name == "response":
            metadata = json.loads(payload)
        else:
            files[name] = payload
    return metadata, files
