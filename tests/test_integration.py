import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from fomo.client import Client
from fomo.client.transports.http import HttpTransport
from fomo.runtime.registry import SKTIME_REGISTRY
from fomo.server import Server
from fomo.types import HealthResult, ModelInfo, StatsResult


def create_client(load_models=["naive"]):
    server = Server(load_models=load_models)
    app = server.app
    httpx_client = TestClient(app)
    client = Client(
        server.url,
        transport=HttpTransport(server.url, httpx_client=httpx_client),
    )
    return client


client = create_client()

PAST = {
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


def test_predict():
    result = client.predict(
        past=PAST,
        future={
            "timestamp": ["2024-01-06", "2024-01-07", "2024-01-08"],
            "price": [8.99, 9.99, 8.99],
        },
        static={"store_type": ["urban"]},
        time="timestamp",
        target=["sales"],
        fh=3,
        model="naive",
        quantiles=[0.1, 0.5, 0.9],
    )

    assert result.model == "naive"
    assert result.request_id
    assert list(result.predictions["sales"]) == [142.5, 147.0, 151.5]
    assert result.quantiles is not None
    assert len(result.quantiles["timestamp"]) == 3


def test_predict_unknown_model():
    with pytest.raises(RuntimeError, match="chronos-2"):
        client.predict(
            past=PAST,
            time="timestamp",
            target=["sales"],
            fh=3,
            model="chronos-2",
        )


def test_predict_sktime_parity():
    pytest.importorskip("transformers")
    pytest.importorskip("torch")

    from sktime.datasets import load_longley
    from sktime.registry import craft
    from sktime.split import temporal_train_test_split

    model = "ttm-r3"
    fh = 2
    y, X = load_longley()
    y_train, _, X_train, X_future = temporal_train_test_split(y, X, test_size=fh)

    sktime_pred = (
        craft(SKTIME_REGISTRY[model]["spec"])
        .fit(y_train, X=X_train, fh=list(range(1, fh + 1)))
        .predict(X=X_future)
    )

    past = pd.concat([y_train.to_frame(), X_train], axis=1).reset_index()
    future = X_future.reset_index()
    past["Period"] = past["Period"].dt.to_timestamp()
    future["Period"] = future["Period"].dt.to_timestamp()

    ttm_client = create_client(load_models=[model])
    result = ttm_client.predict(
        past=past,
        future=future,
        time="Period",
        target=["TOTEMP"],
        fh=fh,
        model=model,
    )

    assert result.model == model
    assert result.request_id
    np.testing.assert_allclose(
        result.predictions["TOTEMP"].to_numpy(),
        sktime_pred.to_numpy().reshape(-1),
        rtol=1e-5,
        atol=1e-4,
    )
