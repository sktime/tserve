from typing import Any

import narwhals as nw
import pandas as pd

from fomo.runtime.registry import get_model
from fomo.runtime.types import ForecastJob
from fomo.runtime.types import ForecastResult as RuntimeForecastResult
from fomo.types import ForecastRequest, ForecastResult


def _as_table_dict(table: Any) -> dict[str, Any]:
    if hasattr(table, "model_dump"):
        table = table.model_dump()
    return table


def table_to_frame(table: Any) -> nw.DataFrame:
    data = _as_table_dict(table)
    cols = {name: [row[i] for row in data["data"]] for i, name in enumerate(data["columns"])}
    return nw.from_dict(cols, backend="pandas")


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
        model_config=dict(request.model_params or {}),
    )
    validate_job(job)
    return job


def result_to_response(result: RuntimeForecastResult) -> ForecastResult:
    return ForecastResult(
        predictions=frame_to_table(result.y_pred),
        quantiles=frame_to_table(result.quantiles) if result.quantiles is not None else None,
        model=result.model,
        request_id="",
    )
