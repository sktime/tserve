from typing import Any

import narwhals as nw
from narwhals.dependencies import (
    is_pandas_like_dataframe,
    is_polars_dataframe,
    is_pyarrow_table,
)


def _check_frame(value: Any, *, name: str) -> None:
    if value is None:
        return
    if type(value) is dict:
        if all(isinstance(k, str) and isinstance(v, list) for k, v in value.items()):
            return
        raise ValueError(f"{name} must be dict[str, list]")
    if (
        isinstance(value, nw.DataFrame)
        or is_pandas_like_dataframe(value)
        or is_polars_dataframe(value)
        or is_pyarrow_table(value)
    ):
        return
    raise ValueError(
        f"{name} must be a supported dataframe or dict[str, list], "
        f"got {type(value).__name__}"
    )


def _require_columns(
    frame: nw.DataFrame[Any], columns: list[str], *, frame_name: str
) -> None:
    missing = [name for name in columns if name not in frame.columns]
    if missing:
        raise ValueError(f"{frame_name} is missing columns: {missing}")
