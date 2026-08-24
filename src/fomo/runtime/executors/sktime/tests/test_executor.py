import narwhals as nw
from sktime.forecasting.naive import NaiveForecaster

from fomo.runtime.executors.sktime.executor import SktimeExecutor
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
        "horizon": 1,
        "context": 3,
        "model": "naive",
    }
    payload.update(kwargs)
    return CoercedForecastRequest.model_validate(payload)


def test_load():
    executor = SktimeExecutor()

    executor.load(ModelInfo(id="naive", executor="sktime", source="registry"), "naive")

    assert type(executor._forecaster) is NaiveForecaster
    assert executor.load_s is not None
    assert executor.warmup_s is not None


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

    assert type(executor._forecaster) is NaiveForecaster


def test_predict():
    executor = SktimeExecutor()
    executor.load(ModelInfo(id="naive", executor="sktime", source="registry"), "naive")

    response = executor.predict(_request())

    assert type(response) is CoercedForecastResponse
    assert type(response.predictions) is nw.DataFrame
    assert response.model == "naive"
