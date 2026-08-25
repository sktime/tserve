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


def test_health():
    assert client.health() == HealthResult(status="ok")


def test_models():
    assert client.models().models == [
        ModelInfo(id="naive", executor="sktime", source="registry")
    ]


def test_stats():
    stats = client.stats()

    assert type(stats) is StatsResult
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
