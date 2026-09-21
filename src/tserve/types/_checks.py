"""Validate user-facing frame values before they are coerced to narwhals.

``PredictRequest`` and ``PredictResponse`` accept several native table
shapes. These helpers reject values that are none of those shapes, so
coercion in ``tserve.types.converters`` can assume a pandas-like, polars,
pyarrow, narwhals, column-dict, or ``{columns, data}`` payload.

Column *presence* (time, target, known-future, …) is checked later on
``CoercedPredictRequest``, after frames are narwhals. This module does
not interpret prediction semantics and does not mention sktime.

See Also
--------
tserve.types.models.PredictRequest
    Construction runs ``_check_frame`` on ``past``, ``future``, and
    ``static``.
tserve.types.converters._to_narwhals
    Converts a frame that has already passed these checks.
"""

from typing import Any

import narwhals as nw
from narwhals.dependencies import (
    is_pandas_like_dataframe,
    is_polars_dataframe,
    is_pyarrow_table,
)

_TABLE_SHAPE = (
    "{'columns': [...], 'data': [[...], ...]} or a dict of column name -> list"
)


def _check_frame(value: Any, *, name: str) -> None:
    """Accept a supported table, ``None``, or raise ``ValueError``.

    Supported values are a narwhals DataFrame, a pandas-like DataFrame, a
    polars DataFrame, a pyarrow Table, a column-oriented ``dict`` of name
    to list, or a row-oriented ``{"columns": [...], "data": [[...], ...]}``
    dict. ``None`` is allowed so optional request fields (``future``,
    ``static``, ``quantiles``) can be omitted.

    Parameters
    ----------
    value : any
        Candidate frame or ``None``.
    name : str
        Field name used in error messages (``"past"``, ``"future"``,
        ``"static"``, ``"predictions"``, ``"quantiles"``).

    Raises
    ------
    ValueError
        If ``value`` is not ``None`` and not one of the supported shapes.
        Dict payloads are delegated to ``_check_frame_dict``.
    """
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
    """Validate a dict-shaped table as either row-oriented or column-oriented.

    A dict with both ``"columns"`` and ``"data"`` is treated as a row
    matrix and passed to ``_check_columns_data``. Any other dict must map
    string column names to lists of equal length (column-oriented).

    Parameters
    ----------
    value : dict
        Frame payload from JSON or a Python caller.
    name : str
        Field name used in error messages.

    Raises
    ------
    ValueError
        If a row-oriented dict has extra keys besides ``columns`` and
        ``data``; if the dict is empty; if keys are not strings; if
        values are not lists; or if column lengths differ.
    """
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
        raise ValueError(f"{name} column values must be lists, got {not_lists}")

    lengths = {key: len(values) for key, values in value.items()}
    if len(set(lengths.values())) > 1:
        raise ValueError(
            f"{name} columns must have the same number of rows, got {lengths}"
        )


def _check_columns_data(value: dict[Any, Any], *, name: str) -> None:
    """Validate a ``{columns, data}`` row-oriented table.

    Parameters
    ----------
    value : dict
        Mapping with ``"columns"`` (list of str) and ``"data"`` (list of
        rows). Each row must be a list whose length matches ``columns``.
    name : str
        Field name used in error messages.

    Raises
    ------
    ValueError
        If ``columns`` is not a list of strings, ``data`` is not a list
        of lists, or a row has the wrong width.
    """
    columns, data = value["columns"], value["data"]

    if not isinstance(columns, list) or not all(
        isinstance(col, str) for col in columns
    ):
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
    """Require named columns to exist on a coerced narwhals frame.

    Used by ``CoercedPredictRequest`` after wire conversion, not by
    user-facing ``PredictRequest`` (which only checks table *shape*).

    Parameters
    ----------
    frame : narwhals.DataFrame
        Coerced table.
    columns : list of str
        Required column names, in any order relative to the frame.
    frame_name : str
        Field name used in error messages (``"past"``, ``"future"``,
        ``"static"``).

    Raises
    ------
    ValueError
        If any name in ``columns`` is missing. The message lists missing
        and available columns.
    """
    missing = [name for name in columns if name not in frame.columns]
    if missing:
        available = list(frame.columns)
        raise ValueError(
            f"{frame_name} is missing columns: {missing} (available: {available})"
        )
