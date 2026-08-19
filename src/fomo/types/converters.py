from typing import Any

import narwhals as nw
import pandas as pd

from fomo.runtime.registry import get_model
from fomo.types.models import ForecastJob, ForecastRequest, ForecastResponse, ForecastResult


_JSON_ROWS = "json_rows"
_JSON_COLUMNS = "json_columns"
_NARWHALS = "narwhals"

TableFormat = str | nw.Implementation
"""How a caller encoded a table: a JSON layout, Narwhals, or a native backend."""


def _as_table_dict(table: Any) -> dict[str, Any]:
    if hasattr(table, "model_dump"):
        table = table.model_dump()
    return table


def is_json_table(table: Any) -> bool:
    """Return whether a table can travel directly through the JSON transport."""
    if not isinstance(table, dict):
        return False
    if "columns" in table and "data" in table:
        return isinstance(table["columns"], list) and isinstance(table["data"], list)
    return bool(table) and all(isinstance(value, list) for value in table.values())


def as_frame(table: Any) -> nw.DataFrame:
    """Convert any Narwhals-supported dataframe (or pass through an existing frame)."""
    if isinstance(table, nw.DataFrame):
        return table
    return nw.from_native(table, eager_only=True)


def table_format(table: Any) -> TableFormat:
    """Describe how a table is encoded, so results can be returned in the same shape."""
    data = _as_table_dict(table) if hasattr(table, "model_dump") else table
    if is_json_table(data):
        return _JSON_ROWS if "columns" in data and "data" in data else _JSON_COLUMNS
    if isinstance(table, nw.DataFrame):
        return _NARWHALS
    return as_frame(table).implementation


def table_to_frame(table: Any) -> nw.DataFrame:
    """Accept JSON table dicts or any Narwhals-supported dataframe."""
    data = _as_table_dict(table) if hasattr(table, "model_dump") else table
    fmt = table_format(data)
    if fmt == _JSON_ROWS:
        cols = {name: [row[i] for row in data["data"]] for i, name in enumerate(data["columns"])}
        return nw.from_dict(cols, backend="pandas")
    if fmt == _JSON_COLUMNS:
        return nw.from_dict(data, backend="pandas")
    return as_frame(table)


def _json_cell(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def frame_to_table(frame: nw.DataFrame) -> dict[str, Any]:
    return {
        "columns": list(frame.columns),
        "data": [[_json_cell(cell) for cell in row] for row in frame.iter_rows()],
    }


def frame_to_columns(frame: nw.DataFrame) -> dict[str, list[Any]]:
    return {name: [_json_cell(cell) for cell in frame[name].to_list()] for name in frame.columns}


def frame_to_format(frame: nw.DataFrame, fmt: TableFormat) -> Any:
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
        return frame_to_columns(frame)
    raise ValueError(f"unknown table format {fmt!r}")


def _index_columns(request: ForecastRequest) -> list[str]:
    return list(request.series_id or []) + [request.time]


def _parse_time(frame: nw.DataFrame, time: str) -> nw.DataFrame:
    pdf = frame.to_pandas()
    pdf[time] = pd.to_datetime(pdf[time])
    return nw.from_native(pdf, eager_only=True)


def _select(frame: nw.DataFrame, columns: list[str]) -> nw.DataFrame:
    keep = [col for col in columns if col in frame.columns]
    return frame.select(keep)


def _join_static(
    frame: nw.DataFrame,
    static: nw.DataFrame,
    series_id: list[str],
) -> nw.DataFrame:
    return frame.join(static, on=series_id, how="left")


def _future_index_from_freq(request: ForecastRequest, hist: pd.DataFrame) -> pd.DataFrame:
    if request.freq is None:
        raise ValueError("freq is required when static is set without future")
    keys = list(request.series_id or [])
    rows: list[list[Any]] = []
    if keys:
        for key, group in hist.groupby(keys, sort=False):
            key_t = key if isinstance(key, tuple) else (key,)
            last = group[request.time].max()
            times = pd.date_range(last, periods=request.horizon + 1, freq=request.freq)[1:]
            for ts in times:
                rows.append([*key_t, ts])
    else:
        last = hist[request.time].max()
        times = pd.date_range(last, periods=request.horizon + 1, freq=request.freq)[1:]
        rows.extend([ts] for ts in times)
    return pd.DataFrame(rows, columns=keys + [request.time])


def validate_job(job: ForecastJob) -> None:
    spec = get_model(job.model)
    if len(job.target) > 1 and not spec.multivariate:
        raise ValueError(f"model {job.model!r} does not support multivariate targets")
    has_exog = job.X is not None or job.X_future is not None
    if has_exog and not spec.exogenous:
        raise ValueError(f"model {job.model!r} does not support exogenous data")
    if job.quantiles and not spec.quantiles:
        raise ValueError(f"model {job.model!r} does not support quantile forecasts")


def job_from_request(request: ForecastRequest) -> ForecastJob:
    index_cols = _index_columns(request)
    hist = _parse_time(table_to_frame(request.history), request.time)
    y = _select(hist, index_cols + list(request.target))

    known = list(request.known_future or [])
    x: nw.DataFrame | None = None
    x_future: nw.DataFrame | None = None

    if known or request.static is not None:
        x = _select(hist, index_cols + known)
        if request.future is not None:
            fut = _parse_time(table_to_frame(request.future), request.time)
            x_future = _select(fut, index_cols + known)
        else:
            x_future = nw.from_native(
                _future_index_from_freq(request, hist.to_pandas()),
                eager_only=True,
            )

        if request.static is not None:
            assert request.series_id is not None
            static = table_to_frame(request.static)
            x = _join_static(x, static, request.series_id)
            x_future = _join_static(x_future, static, request.series_id)

    job = ForecastJob(
        model=request.model,
        y=y,
        horizon=request.horizon,
        target=tuple(request.target),
        time=request.time,
        series_id=tuple(request.series_id or ()),
        X=x,
        X_future=x_future,
        past_only=tuple(request.past_only or ()),
        freq=request.freq,
        quantiles=tuple(request.quantiles) if request.quantiles else None,
        params=dict(request.params or {}),
    )
    validate_job(job)
    return job


def result_to_response(result: ForecastResult) -> ForecastResponse:
    return ForecastResponse(
        predictions=frame_to_table(result.y_pred),
        quantiles=frame_to_table(result.quantiles) if result.quantiles is not None else None,
        model=result.model,
        request_id="",
    )


def result_to_frame_response(result: ForecastResult) -> ForecastResponse:
    """Return a response whose table values stay as Narwhals DataFrames."""
    return ForecastResponse(
        predictions=as_frame(result.y_pred),
        quantiles=as_frame(result.quantiles) if result.quantiles is not None else None,
        model=result.model,
        request_id="",
    )
