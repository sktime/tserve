"""Wire and coerced predict models shared by the client, server, and runtime.

TServe splits every prediction into two representations. User-facing models
(``PredictRequest``, ``PredictResponse``) accept native frames — pandas,
polars, pyarrow, narwhals, a column dict, or a ``{columns, data}`` row
matrix. Internal models (``CoercedPredictRequest``,
``CoercedPredictResponse``) hold narwhals frames plus column contracts.
Executors and the scheduler only see the coerced form.

This package is the shared vocabulary for that contract. Frame checking
lives in ``tserve.types._checks``; native ↔ narwhals ↔ Arrow IPC ↔ ``TServe``
envelope conversion lives in ``tserve.types.converters`` (the *wire*
converters). Mapping a coerced request onto sktime ``(y, X, fh)`` is a
different layer: ``tserve.runtime.executors.sktime.converters``.

See Also
--------
tserve.types.models
    Pydantic request, response, health, listing, and stats schemas.
tserve.types.converters
    Coerce, encode, decode, and pack frames for HTTP JSON and bytes paths.
"""

from tserve.types.models import (
    CoercedPredictRequest,
    CoercedPredictResponse,
    HealthError,
    HealthResult,
    ModelInfo,
    ModelsResult,
    PredictRequest,
    PredictResponse,
    StatsResult,
)

__all__ = [
    "CoercedPredictRequest",
    "CoercedPredictResponse",
    "HealthError",
    "HealthResult",
    "ModelInfo",
    "ModelsResult",
    "PredictRequest",
    "PredictResponse",
    "StatsResult",
]
