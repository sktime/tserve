from typing import Any

import narwhals as nw
import pandas as pd

from fomo.types.models import ForecastRequest, ForecastResponse


_JSON_ROWS = "json_rows"
_JSON_COLUMNS = "json_columns"
_NARWHALS = "narwhals"

TableFormat = str | nw.Implementation
"""How a caller encoded a table: a JSON layout, Narwhals, or a native backend."""


def is_json_table(table: Any) -> bool:
    """Return whether a table can travel directly through the JSON transport."""
    if not isinstance(table, dict):
        return False
    if "columns" in table and "data" in table:
        return isinstance(table["columns"], list) and isinstance(table["data"], list)
    return bool(table) and all(isinstance(value, list) for value in table.values())


def as_frame(table: Any) -> nw.DataFrame[Any]:
    """Convert any Narwhals-supported dataframe (or pass through an existing frame)."""
    if isinstance(table, nw.DataFrame):
        return table
    return nw.from_native(table, eager_only=True)


def table_format(table: Any) -> TableFormat:
    """Describe how a table is encoded, so results can be returned in the same shape."""
    if hasattr(table, "model_dump"):
        table = table.model_dump()
    if is_json_table(table):
        return _JSON_ROWS if "columns" in table and "data" in table else _JSON_COLUMNS
    if isinstance(table, nw.DataFrame):
        return _NARWHALS
    return as_frame(table).implementation


def table_to_frame(table: Any) -> nw.DataFrame[Any]:
    """Accept JSON table dicts, in either layout, or any Narwhals-supported dataframe."""
    if hasattr(table, "model_dump"):
        table = table.model_dump()
    if not is_json_table(table):
        return as_frame(table)
    if "columns" in table and "data" in table:
        table = {
            name: [row[i] for row in table["data"]] for i, name in enumerate(table["columns"])
        }
    return nw.from_dict(table, backend="pandas")


def frame_to_table(frame: nw.DataFrame[Any]) -> dict[str, Any]:
    """Render a frame as a JSON `{columns, data}` table."""
    return {
        "columns": list(frame.columns),
        "data": [[_json_cell(cell) for cell in row] for row in frame.iter_rows()],
    }


def frame_to_format(frame: nw.DataFrame[Any], fmt: TableFormat) -> Any:
    """Render a frame in a format reported by `table_format`, inverting `table_to_frame`."""
    if isinstance(fmt, nw.Implementation):
        if fmt is frame.implementation:
            return frame.to_native()
        return nw.from_arrow(frame.to_arrow(), backend=fmt.to_native_namespace()).to_native()
    if fmt == _NARWHALS:
        return frame
    if fmt == _JSON_ROWS:
        return frame_to_table(frame)
    if fmt == _JSON_COLUMNS:
        return {
            name: [_json_cell(cell) for cell in frame[name].to_list()] for name in frame.columns
        }
    raise ValueError(f"unknown table format {fmt!r}")


def request_to_frames(request: ForecastRequest) -> ForecastRequest:
    """Normalize JSON or native tables on a request into Narwhals DataFrames."""
    return request.model_copy(
        update={
            "history": table_to_frame(request.history),
            "future": table_to_frame(request.future) if request.future is not None else None,
            "static": table_to_frame(request.static) if request.static is not None else None,
        }
    )


def response_to_tables(response: ForecastResponse) -> ForecastResponse:
    """Render response frames as JSON `{columns, data}` tables."""
    return response.model_copy(
        update={
            "predictions": frame_to_table(as_frame(response.predictions)),
            "quantiles": (
                frame_to_table(as_frame(response.quantiles))
                if response.quantiles is not None
                else None
            ),
        }
    )


def _json_cell(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value
