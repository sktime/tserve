"""Wire converters: native frames ↔ narwhals ↔ Arrow IPC ↔ FOMO envelope.

This module is the *wire* layer. It does not map requests onto sktime
``(y, X, fh)`` — that is ``fomo.runtime.executors.sktime.converters``.

Typical paths:

* JSON ``POST /predict``: ``PredictRequest`` → ``coerce_request`` →
  ``Scheduler.run`` → ``Executor.predict`` → column-dict JSON.
* Bytes ``POST /predict/bytes`` (server): multipart metadata + Arrow
  files → ``decode_request`` → ``Scheduler.run`` → ``encode_response``
  → ``pack_envelope``.
* ``Client.predict``: ``coerce_request`` → ``encode_request`` →
  ``BaseTransport.predict`` → ``decode_response`` →
  ``_from_narwhals``. The default transport is ``HttpTransport``
  (``POST /predict/bytes`` + ``unpack_envelope``).

``Client.predict`` also calls ``_from_narwhals`` so returned tables
match the caller's ``past`` native type.

See Also
--------
fomo.types.models.PredictRequest
    Field semantics for the payload split into metadata vs frames.
fomo.runtime.executors.sktime.converters
    Domain converters used only inside the sktime executor.
"""

import io
import json
import struct
from typing import Any

import narwhals as nw
import pyarrow as pa
from narwhals.typing import IntoFrame

from fomo.types.models import (
    CoercedPredictRequest,
    CoercedPredictResponse,
    PredictRequest,
    PredictResponse,
)


def _to_narwhals(
    df: IntoFrame | dict[str, list], *, name: str = "table"
) -> nw.DataFrame:
    """Convert a supported native table into a narwhals DataFrame.

    Parameters
    ----------
    df : narwhals.DataFrame, mapping, or into-frame
        Already-narwhals frames are returned unchanged. A dict with
        exactly ``{"columns", "data"}`` is read as a row matrix via
        ``narwhals.from_dicts``. Any other dict is column-oriented
        (name → list) via ``narwhals.from_dict``. Other values go
        through ``narwhals.from_native(..., eager_only=True)``.
    name : str, default "table"
        Field name (``past``, ``future``, …) used in error messages.

    Returns
    -------
    narwhals.DataFrame
        Eager narwhals frame, pyarrow-backed when built from dicts.

    Raises
    ------
    Exception
        Narwhals/pyarrow errors if ``df`` cannot be interpreted as a
        table. Shape should already have been checked by
        ``PredictRequest`` / ``PredictResponse``.
    """
    if isinstance(df, nw.DataFrame):
        return df

    if isinstance(df, dict):
        try:
            if set(df.keys()) == {"data", "columns"}:
                rows = [
                    dict(zip(df["columns"], row, strict=True))
                    for row in df["data"]
                ]
                return nw.from_dicts(rows, backend="pyarrow")

            return nw.from_dict(df, backend="pyarrow")

        except pa.ArrowInvalid as error:
            raise ValueError(
                f"{name} has a column FoMo could not convert to a single Arrow type.\n\n"
                f"Original error: {error}\n\nEvery value in a column must share one type. "
                'Mixed types (e.g. 1 and "2"), or nested objects and lists in a cell, '
                "cannot be stored; use null for missing values."
            ) from error

    # IntoFrame includes lazy frames; narwhals overloads don't match after
    # the dict branch, but eager_only=True is the documented conversion.
    return nw.from_native(df, eager_only=True)  # ty: ignore[no-matching-overload]


def _from_narwhals(df: nw.DataFrame, template: Any) -> Any:
    """Convert a narwhals frame back to the native type of ``template``.

    Used by ``Client.predict`` so ``predictions`` / ``quantiles`` match
    the caller's ``past`` (pandas, polars, pyarrow, narwhals, dict, …).

    Parameters
    ----------
    df : narwhals.DataFrame
        Table to convert.
    template : any
        Original native object. If it is a ``{columns, data}`` dict, the
        result is that row-oriented shape. If it is any other dict, the
        result is a column dict (name → list). A narwhals DataFrame is
        restored as narwhals (same native backend as ``template``).
        pandas-like, polars, and pyarrow templates use ``to_pandas``,
        ``to_polars``, and ``to_arrow`` respectively.

    Returns
    -------
    any
        Native table of the same kind as ``template``.

    Raises
    ------
    Exception
        Narwhals conversion errors for unsupported templates.
    """
    if isinstance(template, dict):
        as_dict = df.to_dict(as_series=False)
        if set(template) == {"data", "columns"}:
            return {
                "columns": list(as_dict),
                "data": [list(row) for row in zip(*as_dict.values(), strict=True)],
            }
        return as_dict

    if isinstance(template, nw.DataFrame):
        return nw.from_native(_from_narwhals(df, template.to_native()), eager_only=True)

    impl = nw.from_native(template, eager_only=True).implementation
    if impl.is_pandas_like():
        return df.to_pandas()
    if impl.is_polars():
        return df.to_polars()
    if impl.is_pyarrow():
        return df.to_arrow()

    return df.to_native()


def _to_bytes(df: nw.DataFrame) -> bytes:
    """Serialize a narwhals frame as an Arrow IPC stream.

    Parameters
    ----------
    df : narwhals.DataFrame
        Frame to write (converted with ``to_arrow()``).

    Returns
    -------
    bytes
        Arrow IPC stream bytes. Multipart parts use content type
        ``application/vnd.apache.arrow.stream``; the packed envelope
        uses media type ``application/vnd.fomo.predict+arrow``.
    """
    df = df.to_arrow()
    sink = io.BytesIO()
    with pa.ipc.new_stream(sink, df.schema) as writer:
        writer.write_table(df)
    return sink.getvalue()


def _from_arrow_bytes(blob: bytes, *, name: str) -> nw.DataFrame:
    """Read one Arrow IPC stream blob back into a narwhals DataFrame.

    Inverse of ``_to_bytes`` for the multipart and envelope paths.

    Parameters
    ----------
    blob : bytes
        Arrow IPC stream bytes for a single named part.
    name : str
        Part name (``past``, ``predictions``, …) used in error messages.

    Returns
    -------
    narwhals.DataFrame
        Eager pyarrow-backed frame.

    Raises
    ------
    ValueError
        If ``blob`` is not a readable Arrow IPC stream (empty body,
        text, or truncated bytes). Re-raised from the ``pyarrow.ArrowInvalid``.
    """
    try:
        table = pa.ipc.open_stream(io.BytesIO(blob)).read_all()

    except pa.ArrowInvalid as error:
        raise ValueError(
            f"{name} could not be read as an Arrow IPC stream.\n\nOriginal error: "
            f"{error}\n\nEach frame part of a multipart POST /predict/bytes must be "
            "the bytes of an Arrow IPC *stream* (pyarrow.ipc.new_stream), not an "
            "empty body, a JSON body, or an Arrow *file*. The FoMo client writes "
            "this format for you."
        ) from error

    return nw.from_arrow(table, backend="pyarrow")


def coerce_request(request: PredictRequest) -> CoercedPredictRequest:
    """Turn a user-facing request into the narwhals form executors consume.

    Copies scalar metadata with ``model_dump``, converts ``past`` /
    ``future`` / ``static`` via ``_to_narwhals``, then fills omitted
    ``time`` / ``target`` and validates ``CoercedPredictRequest``
    (column contracts).

    When ``time`` is omitted, the first column of ``past`` is used.
    When ``target`` is a string, it becomes a one-element list. When
    ``target`` is omitted, every ``past`` column other than ``time``
    and the column names of ``future`` (if present) is inferred.

    Parameters
    ----------
    request : PredictRequest
        User-facing predict input (JSON body or ``Client.predict``).

    Returns
    -------
    CoercedPredictRequest
        Internal request with narwhals frames.

    Raises
    ------
    ValidationError
        If coerced frames fail column checks (missing time/target
        columns), inferred ``target`` is empty, or dumped fields
        cannot construct ``CoercedPredictRequest``. Inner validators
        raise ``ValueError``, which Pydantic wraps.
    ValueError
        If ``time`` is omitted and ``past`` has no columns.
    Exception
        If a frame cannot be converted to narwhals.

    See Also
    --------
    CoercedPredictRequest
        Column contracts applied here.
    encode_request
        Next step on the bytes path.
    """
    payload = request.model_dump(exclude={"past", "future", "static"})
    past = _to_narwhals(request.past, name="past")
    future = (
        _to_narwhals(request.future, name="future")
        if request.future is not None
        else None
    )
    payload["past"] = past
    payload["future"] = future
    payload["static"] = (
        _to_narwhals(request.static, name="static")
        if request.static is not None
        else None
    )

    if payload["time"] is None:
        if not past.columns:
            raise ValueError("time is omitted but past has no columns")
        payload["time"] = past.columns[0]

    target = payload["target"]
    if target is None:
        future_cols = set(future.columns) if future is not None else set()
        payload["target"] = [
            col
            for col in past.columns
            if col != payload["time"] and col not in future_cols
        ]
    elif isinstance(target, str):
        payload["target"] = [target]

    return CoercedPredictRequest.model_validate(payload)


def encode_request(request: CoercedPredictRequest) -> tuple[dict, dict[str, bytes]]:
    """Split a coerced request into JSON metadata and Arrow IPC files.

    Frame fields ``past``, ``future``, and ``static`` become named
    byte blobs when not ``None``. Remaining fields (``time``, ``target``,
    ``fh``, ``model``, …) stay in the metadata dict
    for the multipart ``metadata`` form field.

    Parameters
    ----------
    request : CoercedPredictRequest
        Coerced predict input.

    Returns
    -------
    metadata : dict
        JSON-serializable fields, excluding encoded frames.
    bytes_encoded : dict of str to bytes
        Mapping of frame name (``past`` / ``future`` / ``static``)
        to Arrow IPC stream bytes.

    See Also
    --------
    decode_request
        Inverse used by ``POST /predict/bytes``.
    """
    bytes_encoded = {}
    for frame in ["past", "future", "static"]:
        value = getattr(request, frame)
        if value is not None:
            bytes_encoded[frame] = _to_bytes(value)

    metadata = request.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_request(
    metadata: dict, bytes_encoded: dict[str, bytes]
) -> CoercedPredictRequest:
    """Rebuild a coerced request from metadata plus Arrow IPC files.

    Parameters
    ----------
    metadata : dict
        JSON object from the multipart ``metadata`` field (non-frame
        predict fields such as ``time``, ``target``, ``fh``,
        ``model``).
    bytes_encoded : dict of str to bytes
        Optional ``past``, ``future``, ``static`` Arrow IPC streams.

    Returns
    -------
    CoercedPredictRequest
        Validated internal request.

    Raises
    ------
    ValidationError
        If column contracts fail after frames are attached, or
        metadata types are invalid. Inner validators raise
        ``ValueError``, which Pydantic wraps.
    Exception
        If an IPC blob is not a readable Arrow stream.

    See Also
    --------
    encode_request
        Inverse used by ``Client.predict``.
    """
    payload = dict(metadata)
    for frame in ["past", "future", "static"]:
        if frame in bytes_encoded:
            payload[frame] = _from_arrow_bytes(bytes_encoded[frame], name=frame)
    return CoercedPredictRequest.model_validate(payload)


def coerce_response(response: PredictResponse) -> CoercedPredictResponse:
    """Turn a user-facing response into narwhals prediction tables.

    Parameters
    ----------
    response : PredictResponse
        User-facing predict output.

    Returns
    -------
    CoercedPredictResponse
        Internal response with narwhals frames.

    Raises
    ------
    ValueError
        If prediction tables have no columns after conversion.
    ValidationError
        If dumped fields cannot construct ``CoercedPredictResponse``.
    Exception
        If a frame cannot be converted to narwhals.
    """
    payload = response.model_dump(exclude={"predictions", "quantiles"})
    payload["predictions"] = _to_narwhals(response.predictions, name="predictions")
    payload["quantiles"] = (
        _to_narwhals(response.quantiles, name="quantiles")
        if response.quantiles is not None
        else None
    )
    return CoercedPredictResponse.model_validate(payload)


def encode_response(response: CoercedPredictResponse) -> tuple[dict, dict[str, bytes]]:
    """Split a coerced response into JSON metadata and Arrow IPC files.

    Parameters
    ----------
    response : CoercedPredictResponse
        Executor output (``request_id`` should already be set by the
        bytes route when used from the server).

    Returns
    -------
    metadata : dict
        JSON-serializable fields, excluding encoded frames.
    bytes_encoded : dict of str to bytes
        ``predictions`` and, when present, ``quantiles`` as Arrow IPC.

    See Also
    --------
    pack_envelope
        Wraps this pair in the ``FOMO`` binary envelope.
    """
    bytes_encoded = {}
    for frame in ["predictions", "quantiles"]:
        value = getattr(response, frame)
        if value is not None:
            bytes_encoded[frame] = _to_bytes(value)

    metadata = response.model_dump(exclude=set(bytes_encoded.keys()))

    return metadata, bytes_encoded


def decode_response(
    metadata: dict, bytes_encoded: dict[str, bytes]
) -> CoercedPredictResponse:
    """Rebuild a coerced response from metadata plus Arrow IPC files.

    Parameters
    ----------
    metadata : dict
        JSON object from the envelope ``response`` part.
    bytes_encoded : dict of str to bytes
        ``predictions`` and optional ``quantiles`` Arrow IPC streams.

    Returns
    -------
    CoercedPredictResponse
        Validated internal response.

    Raises
    ------
    ValueError
        If prediction tables have no columns.
    ValidationError
        If metadata types are invalid.
    Exception
        If an IPC blob is not a readable Arrow stream.
    """
    payload = dict(metadata)
    for frame in ["predictions", "quantiles"]:
        if frame in bytes_encoded:
            payload[frame] = _from_arrow_bytes(bytes_encoded[frame], name=frame)
    return CoercedPredictResponse.model_validate(payload)


def pack_envelope(metadata: dict, files: dict[str, bytes]) -> bytes:
    """Pack response metadata and Arrow blobs into a ``FOMO`` envelope.

    Layout: magic ``b"FOMO"``, version byte ``1``, little-endian
    ``uint32`` part count, then for each part name length, name bytes,
    payload length, payload. The first part is always named
    ``"response"`` and holds ``json.dumps(metadata)``. Remaining parts
    are the ``files`` mapping (typically ``predictions`` / ``quantiles``).

    Parameters
    ----------
    metadata : dict
        JSON-serializable response fields from ``encode_response``.
    files : dict of str to bytes
        Named Arrow IPC blobs.

    Returns
    -------
    bytes
        Envelope body. Server sets media type
        ``application/vnd.fomo.predict+arrow``.

    See Also
    --------
    unpack_envelope
        Inverse used by ``HttpTransport.predict``.
    """
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
    """Parse a ``FOMO`` version-1 envelope into metadata and file parts.

    Parameters
    ----------
    body : bytes
        Raw HTTP response body from ``POST /predict/bytes``.

    Returns
    -------
    metadata : dict
        JSON object from the ``response`` part (empty dict if missing).
    files : dict of str to bytes
        All other parts (frame name → payload).

    Raises
    ------
    ValueError
        If the buffer is truncated, magic is not ``FOMO``, or the
        version byte is not ``1``.
    json.JSONDecodeError
        If the ``response`` part is not valid JSON.
    UnicodeDecodeError
        If a part name is not valid UTF-8.
    """
    if len(body) < 9:
        raise ValueError("invalid predict envelope: truncated")
    if body[:4] != b"FOMO":
        raise ValueError("invalid predict envelope: expected FOMO magic bytes")
    if body[4] != 1:
        raise ValueError(f"invalid predict envelope: unsupported version {body[4]}")
    n_parts = struct.unpack_from("<I", body, 5)[0]
    offset = 9
    metadata: dict = {}
    files: dict[str, bytes] = {}
    for _ in range(n_parts):
        if offset + 4 > len(body):
            raise ValueError("invalid predict envelope: truncated")
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
