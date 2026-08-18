from __future__ import annotations

FORECAST_REQUEST = {
    "time": "timestamp",
    "target": ["sales"],
    "history": {
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-01", 120],
            ["2024-01-02", 135],
            ["2024-01-03", 128],
            ["2024-01-04", 142],
            ["2024-01-05", 138],
        ],
    },
    "horizon": 3,
    "freq": "D",
    "model": "dummy",
}

FORECAST_RESULT = {
    "predictions": {
        "columns": ["timestamp", "sales"],
        "data": [
            ["2024-01-06T00:00:00", 138.0],
            ["2024-01-07T00:00:00", 138.0],
            ["2024-01-08T00:00:00", 138.0],
        ],
    },
    "quantiles": None,
    "model": "dummy",
    "request_id": "00000000-0000-0000-0000-000000000000",
}

HEALTH_OK = {"status": "ok"}

HEALTH_UNHEALTHY = {
    "status": "unhealthy",
    "error": {
        "code": "MODEL_NOT_LOADED",
        "message": "The forecasting model has not been loaded.",
    },
}

MODEL_INFO = {
    "alias": "dummy",
    "estimator": "NaiveForecaster",
    "executor": "sktime",
    "multivariate": False,
    "exogenous": False,
    "quantiles": True,
}

MODELS_RESULT = {"models": [MODEL_INFO]}

ERROR_RESPONSE = {
    "error": "bad forecast",
    "code": "bad_request",
    "request_id": "00000000-0000-0000-0000-000000000000",
    "details": None,
}
