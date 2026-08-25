import narwhals as nw

from fomo.runtime.executors.dummy.executor import DummyExecutor
from fomo.runtime.executors.plugins import available_executors, create_executor
from fomo.runtime.registry.resolver import resolve_model
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


def _request(**kwargs):
    payload = {
        "history": _df(
            timestamp=["2024-01-01", "2024-01-02", "2024-01-03"],
            sales=[120, 135, 128],
        ),
        "time": "timestamp",
        "target": ["sales"],
        "horizon": 3,
        "context": 3,
        "model": "dummy",
    }
    payload.update(kwargs)
    return CoercedForecastRequest.model_validate(payload)


def test_available_executors_includes_dummy():
    assert "dummy" in available_executors()


def test_create_executor():
    executor = create_executor("dummy")

    assert type(executor) is DummyExecutor


def test_resolve_model_from_registry():
    info = resolve_model("dummy")

    assert info == ModelInfo(id="dummy", executor="dummy", source="registry")


def test_load():
    executor = DummyExecutor()

    executor.load(ModelInfo(id="dummy", executor="dummy", source="registry"), "dummy")

    assert executor.load_s is not None
    assert executor.warmup_s is not None


def test_bootstrap_loads_dummy():
    from fomo.runtime.bootstrap import bootstrap

    runtime = bootstrap(["dummy"])

    assert type(runtime.executors["dummy"]) is DummyExecutor
    assert runtime.models["dummy"] == ModelInfo(
        id="dummy", executor="dummy", source="registry"
    )


def test_predict_repeats_last_observation():
    executor = DummyExecutor()
    executor.load(ModelInfo(id="dummy", executor="dummy", source="registry"), "dummy")

    response = executor.predict(_request())

    assert type(response) is CoercedForecastResponse
    preds = response.predictions.to_dict(as_series=False)
    assert preds["sales"] == [128, 128, 128]
    assert preds["timestamp"] == ["2024-01-04", "2024-01-05", "2024-01-06"]
    assert response.model == "dummy"
    assert response.quantiles is None
