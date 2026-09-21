import narwhals as nw
import pytest
from sktime.forecasting.naive import NaiveForecaster

from tserve.runtime.executors.sktime.executor import SktimeExecutor
from tserve.types.models import CoercedPredictRequest, CoercedPredictResponse, ModelInfo


def _df(**columns):
    return nw.from_dict(columns, backend="pyarrow")


def _request(**kwargs):
    payload = {
        "past": _df(
            timestamp=["2024-01-01", "2024-01-02", "2024-01-03"],
            sales=[120, 135, 128],
        ),
        "time": "timestamp",
        "target": ["sales"],
        "fh": 1,
        "model": "naive",
    }
    payload.update(kwargs)
    return CoercedPredictRequest.model_validate(payload)


def test_load():
    executor = SktimeExecutor()

    executor.load(ModelInfo(id="naive", executor="sktime", source="registry"), "naive")

    assert executor._forecaster is not None
    assert not executor._forecaster.is_fitted


def test_warmup():
    executor = SktimeExecutor()
    executor.load(ModelInfo(id="naive", executor="sktime", source="registry"), "naive")

    executor.warmup()

    assert executor._forecaster.is_fitted


def test_load_object():
    executor = SktimeExecutor()
    model = NaiveForecaster()

    executor.load(ModelInfo(id="mine", executor="sktime", source="object"), model)

    assert executor._forecaster is model


def test_load_craft():
    executor = SktimeExecutor()

    executor.load(
        ModelInfo(id="mine", executor="sktime", source="craft"),
        "NaiveForecaster()",
    )

    assert isinstance(executor._forecaster, NaiveForecaster)
    assert not executor._forecaster.is_fitted


def test_load_craft_rejects_class():
    executor = SktimeExecutor()

    with pytest.raises(TypeError, match="forecaster instance"):
        executor.load(
            ModelInfo(id="mine", executor="sktime", source="craft"),
            "NaiveForecaster",
        )


def test_load_path(tmp_path):
    zip_path = tmp_path / "naive.zip"
    NaiveForecaster().save(tmp_path / "naive")

    executor = SktimeExecutor()
    executor.load(
        ModelInfo(id="naive", executor="sktime", source="directory"), zip_path
    )

    assert isinstance(executor._forecaster, NaiveForecaster)


def test_predict():
    executor = SktimeExecutor()
    executor.load(ModelInfo(id="naive", executor="sktime", source="registry"), "naive")

    response = executor.predict(_request())

    assert isinstance(response, CoercedPredictResponse)
    assert isinstance(response.predictions, nw.DataFrame)
    assert response.model == "naive"
