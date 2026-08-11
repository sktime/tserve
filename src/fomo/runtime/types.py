from dataclasses import dataclass, field
from typing import Any

import narwhals as nw


@dataclass(frozen=True)
class ForecastJob:
    model: str
    y: nw.DataFrame
    horizon: int
    target_columns: tuple[str, ...]
    X: nw.DataFrame | None = None
    X_future: nw.DataFrame | None = None
    time_column: str | None = None
    id_columns: tuple[str, ...] = field(default_factory=tuple)
    freq: str | None = None
    context: int | None = None
    quantiles: tuple[float, ...] | None = None
    model_config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ForecastResult:
    y_pred: nw.DataFrame
    model: str
    quantiles: nw.DataFrame | None = None
