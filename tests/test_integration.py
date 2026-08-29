import pytest
from fastapi.testclient import TestClient

from fomo.client import Client
from fomo.client.transports.http import HttpTransport
from fomo.server import Server
from fomo.types import HealthResult, ModelInfo, StatsResult


def create_client():
    server = Server(load_models=["naive"])
    app = server.app
    httpx_client = TestClient(app)
    client = Client(
        server.url,
        transport=HttpTransport(server.url, httpx_client=httpx_client),
    )
    return client


client = create_client()

HISTORY = {
    "timestamp": [
        "2024-01-01",
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
    ],
    "sales": [120, 135, 128, 142, 138],
    "price": [9.99, 9.49, 9.99, 8.99, 9.99],
    "promo": [0, 1, 0, 1, 0],
}


def test_health():
    assert client.health() == HealthResult(status="ok")


def test_models():
    assert client.models().models == [
        ModelInfo(id="naive", executor="sktime", source="registry")
    ]


def test_stats():
    stats = client.stats()

    assert isinstance(stats, StatsResult)
    assert stats.uptime_s >= 0
    assert "naive" in stats.models
    assert stats.models["naive"].executor == "sktime"


def test_close():
    extra = create_client()
    extra.close()

    with pytest.raises(RuntimeError, match="closed"):
        extra.health()


def test_context_manager():
    with create_client() as extra:
        assert extra.health() == HealthResult(status="ok")

    with pytest.raises(RuntimeError, match="closed"):
        extra.health()


def test_forecast():
    result = client.forecast(
        history=HISTORY,
        future={
            "timestamp": ["2024-01-06", "2024-01-07", "2024-01-08"],
            "price": [8.99, 9.99, 8.99],
        },
        static={"store_type": ["urban"]},
        time="timestamp",
        target=["sales"],
        horizon=3,
        model="naive",
        quantiles=[0.1, 0.5, 0.9],
    )

    assert result.model == "naive"
    assert result.request_id
    assert list(result.predictions["sales"]) == [138.0, 138.0, 138.0]
    assert result.quantiles is not None
    assert len(result.quantiles["timestamp"]) == 3


def test_forecast_unknown_model():
    with pytest.raises(RuntimeError, match="chronos-2"):
        client.forecast(
            history=HISTORY,
            time="timestamp",
            target=["sales"],
            horizon=3,
            model="chronos-2",
        )
