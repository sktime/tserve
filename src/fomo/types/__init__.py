"""Wire and coerced forecast models shared by the client, server, and runtime.

FoMo splits every forecast into two representations. User-facing models
(``ForecastRequest``, ``ForecastResponse``) accept native frames — pandas,
polars, pyarrow, narwhals, a column dict, or a ``{columns, data}`` row
matrix. Internal models (``CoercedForecastRequest``,
``CoercedForecastResponse``) hold narwhals frames plus column contracts.
Executors and the scheduler only see the coerced form.

This package is the shared vocabulary for that contract. Frame checking
lives in ``fomo.types._checks``; native ↔ narwhals ↔ Arrow IPC ↔ ``FOMO``
envelope conversion lives in ``fomo.types.converters`` (the *wire*
converters). Mapping a coerced request onto sktime ``(y, X, fh)`` is a
different layer: ``fomo.runtime.executors.sktime.convertors``.

See Also
--------
fomo.types.models
    Pydantic request, response, health, listing, and stats schemas.
fomo.types.converters
    Coerce, encode, decode, and pack frames for HTTP JSON and bytes paths.
"""

from fomo.types.models import (
    CoercedForecastRequest,
    CoercedForecastResponse,
    ForecastRequest,
    ForecastResponse,
    HealthError,
    HealthResult,
    ModelInfo,
    ModelsResult,
    StatsResult,
)

__all__ = [
    "CoercedForecastRequest",
    "CoercedForecastResponse",
    "ForecastRequest",
    "ForecastResponse",
    "HealthError",
    "HealthResult",
    "ModelInfo",
    "ModelsResult",
    "StatsResult",
]
