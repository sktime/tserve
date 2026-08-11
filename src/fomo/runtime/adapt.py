import narwhals as nw

from fomo.api.schemas import ForecastRequest, ForecastResponse, Table
from fomo.runtime.registry import get_model
from fomo.runtime.types import ForecastJob, ForecastResult


def table_to_frame(table: Table) -> nw.DataFrame:
    if not table.columns:
        raise ValueError("data.columns must not be empty")
    if not table.data:
        raise ValueError("data.data must not be empty")
    cols = {name: [row[i] for row in table.data] for i, name in enumerate(table.columns)}
    return nw.from_dict(cols, backend="pandas")


def frame_to_table(frame: nw.DataFrame) -> Table:
    return Table(columns=list(frame.columns), data=[list(row) for row in frame.iter_rows()])


def _index_columns(time_column: str | None, id_columns: list[str] | None) -> list[str]:
    cols: list[str] = []
    if id_columns:
        cols.extend(id_columns)
    if time_column:
        cols.append(time_column)
    return cols


def _apply_context(frame: nw.DataFrame, context: int | None, time_column: str | None) -> nw.DataFrame:
    if context is None:
        return frame
    if time_column and time_column in frame.columns:
        return frame.sort(time_column).tail(context)
    return frame.tail(context)


def _resolve_target_columns(
    frame: nw.DataFrame,
    *,
    target_columns: list[str] | None,
    time_column: str | None,
    id_columns: list[str] | None,
) -> tuple[str, ...]:
    if target_columns:
        return tuple(target_columns)

    skip = set(_index_columns(time_column, id_columns))
    numeric = [
        col
        for col in frame.columns
        if col not in skip and frame.schema[col].is_numeric()
    ]
    if not numeric:
        raise ValueError("could not infer target columns from data")
    return tuple(numeric)


def _resolve_exog_columns(
    frame: nw.DataFrame,
    *,
    exog_columns: list[str] | None,
    target_columns: tuple[str, ...],
    time_column: str | None,
    id_columns: list[str] | None,
) -> tuple[str, ...]:
    if exog_columns is not None:
        return tuple(exog_columns)
    skip = set(target_columns) | set(_index_columns(time_column, id_columns))
    return tuple(col for col in frame.columns if col not in skip)


def _with_index_columns(
    frame: nw.DataFrame,
    value_columns: tuple[str, ...],
    *,
    time_column: str | None,
    id_columns: list[str] | None,
) -> nw.DataFrame:
    keep = list(value_columns) + _index_columns(time_column, id_columns)
    keep = [col for col in keep if col in frame.columns]
    return frame.select(keep)


def _last_time(y_frame: nw.DataFrame, time_column: str) -> object:
    if time_column not in y_frame.columns:
        raise ValueError(f"time_column {time_column!r} not found in data")
    return y_frame.sort(time_column).tail(1)[time_column][0]


def _split_exog_timeline(
    y_frame: nw.DataFrame,
    exog_frame: nw.DataFrame,
    *,
    time_column: str,
    exog_columns: tuple[str, ...],
    id_columns: list[str] | None,
    horizon: int,
) -> tuple[nw.DataFrame, nw.DataFrame | None]:
    if time_column not in exog_frame.columns:
        raise ValueError(f"time_column {time_column!r} not found in exog_data")

    missing = [col for col in exog_columns if col not in exog_frame.columns]
    if missing:
        raise ValueError(f"exog columns not found in exog_data: {missing}")

    cutoff = _last_time(y_frame, time_column)
    exog = exog_frame.sort(time_column)
    past = exog.filter(nw.col(time_column) <= cutoff)
    future = exog.filter(nw.col(time_column) > cutoff).head(horizon)

    x_past = _with_index_columns(
        past, exog_columns, time_column=time_column, id_columns=id_columns
    )
    if future.shape[0] == 0:
        return x_past, None
    if future.shape[0] < horizon:
        raise ValueError(
            f"exog_data has {future.shape[0]} future rows but horizon={horizon}; "
            "provide known covariates for the full horizon"
        )
    x_future = _with_index_columns(
        future, exog_columns, time_column=time_column, id_columns=id_columns
    )
    return x_past, x_future


def validate_job(job: ForecastJob) -> None:
    spec = get_model(job.model)
    if len(job.target_columns) > 1 and not spec.multivariate:
        raise ValueError(f"model {job.model!r} does not support multivariate targets")
    has_exog = job.X is not None or job.X_future is not None
    if has_exog and not spec.exogenous:
        raise ValueError(f"model {job.model!r} does not support exogenous data")
    if job.quantiles and not spec.quantiles:
        raise ValueError(f"model {job.model!r} does not support quantile forecasts")


def job_from_request(request: ForecastRequest) -> ForecastJob:
    frame = table_to_frame(request.data)
    frame = _apply_context(frame, request.context, request.time_column)

    target_columns = _resolve_target_columns(
        frame,
        target_columns=request.target_columns,
        time_column=request.time_column,
        id_columns=request.id_columns,
    )
    exog_columns = _resolve_exog_columns(
        frame,
        exog_columns=request.exog_columns,
        target_columns=target_columns,
        time_column=request.time_column,
        id_columns=request.id_columns,
    )

    y = _with_index_columns(
        frame,
        target_columns,
        time_column=request.time_column,
        id_columns=request.id_columns,
    )

    x: nw.DataFrame | None = None
    x_future: nw.DataFrame | None = None

    if request.exog_data is not None:
        if not request.time_column:
            raise ValueError("time_column is required when exog_data is provided")
        if not exog_columns:
            raise ValueError("exog_columns is required when exog_data is provided")
        exog_frame = table_to_frame(request.exog_data)
        x, x_future = _split_exog_timeline(
            y,
            exog_frame,
            time_column=request.time_column,
            exog_columns=exog_columns,
            id_columns=request.id_columns,
            horizon=request.horizon,
        )
    elif exog_columns:
        x = _with_index_columns(
            frame,
            exog_columns,
            time_column=request.time_column,
            id_columns=request.id_columns,
        )

    quantiles = tuple(request.quantiles) if request.quantiles else None
    model_config = dict(request.model_config_overrides or {})

    job = ForecastJob(
        model=request.model,
        y=y,
        horizon=request.horizon,
        target_columns=target_columns,
        X=x,
        X_future=x_future,
        time_column=request.time_column,
        id_columns=tuple(request.id_columns or ()),
        freq=request.freq,
        context=request.context,
        quantiles=quantiles,
        model_config=model_config,
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
