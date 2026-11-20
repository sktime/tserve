import time
from concurrent.futures import ThreadPoolExecutor

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


class _SlowNaive(NaiveForecaster):
    """``NaiveForecaster`` whose fit takes as long as a foundation model's."""

    def _fit(self, y, X=None, fh=None):
        fitted = super()._fit(y, X=X, fh=fh)
        time.sleep(0.01)
        return fitted


def test_predict_concurrent_requests_get_their_own_forecast():
    executor = SktimeExecutor()
    executor.load(
        ModelInfo(id="slow", executor="sktime", source="object"), _SlowNaive()
    )

    def forecast(level):
        n_rows = 10 + level
        request = _request(
            past=_df(t=list(range(n_rows)), y=[float(level)] * n_rows),
            time="t",
            target=["y"],
            model="slow",
        )
        return executor.predict(request).predictions.to_dict(as_series=False)

    levels = range(32)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(forecast, levels))

    for level, result in zip(levels, results, strict=True):
        assert result == {"t": [10 + level], "y": [float(level)]}
