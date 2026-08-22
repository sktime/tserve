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
    "context": 5,
    "freq": "D",
    "quantiles": [0.1, 0.5, 0.9],
    "model": "naive",
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
    "quantiles": {
        "columns": ["timestamp", "sales_0.1", "sales_0.5", "sales_0.9"],
        "data": [
            ["2024-01-06T00:00:00", 130.0, 138.0, 145.0],
            ["2024-01-07T00:00:00", 130.0, 138.0, 145.0],
            ["2024-01-08T00:00:00", 130.0, 138.0, 145.0],
        ],
    },
    "model": "naive",
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
    "id": "naive",
    "executor": "sktime",
    "source": "registry",
}

MODELS_RESULT = {"models": [MODEL_INFO]}

STATS_RESULT = {
    "uptime_s": 3600.5,
    "memory": {"cpu_rss_mb": 512.25, "gpu_mb": 1024.0},
    "models": {
        "naive": {
            "executor": "sktime",
            "load_s": 1.24,
            "warmup_s": 0.31,
            "requests": {"total": 12, "ok": 11, "failed": 1},
            "latency_s": {
                "count": 12,
                "total": 1.86,
                "mean": 0.155,
                "fastest": 0.041,
                "slowest": 0.38,
            },
        }
    },
}

ERROR_RESPONSE = {
    "error": "bad forecast",
    "code": "bad_request",
    "request_id": "00000000-0000-0000-0000-000000000000",
    "details": None,
}
