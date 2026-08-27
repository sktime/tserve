from typing import Any

import narwhals as nw
from narwhals.dependencies import (
    is_pandas_like_dataframe,
    is_polars_dataframe,
    is_pyarrow_table,
)

_TABLE_SHAPE = "{'columns': [...], 'data': [[...], ...]} or a dict of column name -> list"


def _check_frame(value: Any, *, name: str) -> None:
    if (
        value is None
        or isinstance(value, nw.DataFrame)
        or is_pandas_like_dataframe(value)
        or is_polars_dataframe(value)
        or is_pyarrow_table(value)
    ):
        return

    if isinstance(value, dict):
        _check_frame_dict(value, name=name)
        return

    raise ValueError(f"{name} must be {_TABLE_SHAPE}, got {type(value).__name__}")


def _check_frame_dict(value: dict[Any, Any], *, name: str) -> None:
    if "columns" in value and "data" in value:
        extra = sorted(set(value) - {"columns", "data"})
        if extra:
            raise ValueError(
                f"{name} has extra keys {extra}; use only 'columns' and 'data', "
                "or a column-oriented dict of name -> list"
            )
        _check_columns_data(value, name=name)
        return

    if not value:
        raise ValueError(f"{name} is empty; send {_TABLE_SHAPE}")

    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{name} must be {_TABLE_SHAPE}")

    not_lists = {
        key: type(values).__name__
        for key, values in value.items()
        if not isinstance(values, list)
    }
    if not_lists:
        raise ValueError(
            f"{name} column values must be lists, got {not_lists}"
        )

    lengths = {key: len(values) for key, values in value.items()}
    if len(set(lengths.values())) > 1:
        raise ValueError(
            f"{name} columns must have the same number of rows, got {lengths}"
        )


def _check_columns_data(value: dict[Any, Any], *, name: str) -> None:
    columns, data = value["columns"], value["data"]

    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        raise ValueError(
            f"{name}['columns'] must be a list of strings, got {type(columns).__name__}"
        )

    if not isinstance(data, list):
        raise ValueError(
            f"{name}['data'] must be a list of rows (list of lists), "
            f"got {type(data).__name__}"
        )

    for index, row in enumerate(data):
        if not isinstance(row, list):
            raise ValueError(
                f"{name}['data'] row {index} must be a list, got {type(row).__name__}"
            )
        if len(row) != len(columns):
            raise ValueError(
                f"{name}['data'] row {index} has {len(row)} values, "
                f"expected {len(columns)} for columns {columns}"
            )


def _require_columns(
    frame: nw.DataFrame[Any], columns: list[str], *, frame_name: str
) -> None:
    missing = [name for name in columns if name not in frame.columns]
    if missing:
        available = list(frame.columns)
        raise ValueError(
            f"{frame_name} is missing columns: {missing} (available: {available})"
        )
