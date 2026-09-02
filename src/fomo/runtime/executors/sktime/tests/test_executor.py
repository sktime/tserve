import narwhals as nw
from sktime.forecasting.naive import NaiveForecaster

from fomo.runtime.executors.sktime.executor import SktimeExecutor
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse, ModelInfo


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
    return CoercedForecastRequest.model_validate(payload)


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

    assert isinstance(response, CoercedForecastResponse)
    assert isinstance(response.predictions, nw.DataFrame)
    assert response.model == "naive"
