from typing import Any

import narwhals as nw
import pandas as pd

from fomo.types.models import ForecastRequest, ForecastResponse

import pyarrow as pa
import io


def _to_narwhals(df: nw.IntoFrame | dict[str, list]) -> nw.DataFrame:
    if type(df) == nw.DataFrame:
        return df
    if type(df) == dict:
        return nw.from_dict(df)
    return nw.from_native(df, eager_only=True)


def _to_bytes(df: nw.DataFrame) -> bytes:
    df = df.to_arrow()
    sink = io.BytesIO()
    with pa.ipc.new_stream(sink, df.schema) as writer:
        writer.write_table(df)
    return sink.getvalue()


def coerce_request(request: ForecastRequest):
    request.history = _to_narwhals(request.history)
    request.future = _to_narwhals(request.future) if request.future is not None else None
    request.static = _to_narwhals(request.static) if request.static is not None else None

    # add more stringent conversions here
    # e.g interpret freq from index
    # add more stringent checks here
    # e.g check if time/target column exists

    return request


def encode_request(request: ForecastRequest) -> tuple[dict, dict[str, bytes]]:
    request = coerce_request(request)

    bytes_encoded = {}
    for frame in ['history', 'future', 'static']:
        if request[frame] is not None:
            bytes_encoded[frame] = _to_bytes(request[frame])

    metadata = request.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_request(metadata: dict, bytes_encoded: dict[str, bytes]) -> ForecastRequest:
    request = ForecastRequest.model_validate(metadata)

    for frame in ['history', 'future', 'static']:
        if frame in bytes_encoded:
            request[frame] = nw.from_arrow(pa.ipc.read_table(io.BytesIO(bytes_encoded[frame])))

    return request


def coerce_response(response: ForecastResponse):
    response.predictions = _to_narwhals(response.predictions)
    response.quantiles = _to_narwhals(response.quantiles) if response.quantiles is not None else None
    return response


def encode_response(response: ForecastResponse) -> tuple[dict, dict[str, bytes]]:
    response = coerce_response(response)

    bytes_encoded = {}
    for frame in ['predictions', 'quantiles']:
        if response[frame] is not None:
            bytes_encoded[frame] = _to_bytes(response[frame])

    metadata = response.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_response(metadata: dict, bytes_encoded: dict[str, bytes]) -> ForecastResponse:
    response = ForecastResponse.model_validate(metadata)
    for frame in ['predictions', 'quantiles']:
        if frame in bytes_encoded:
            response[frame] = nw.from_arrow(pa.ipc.read_table(io.BytesIO(bytes_encoded[frame])))
    return response
