import pytest

from fomo.runtime.executors.base import Executor
from fomo.runtime.executors.plugins import available_executors, create_executor, register
from fomo.runtime.executors.pytorch_forecasting.executor import PytorchForecastingExecutor
from fomo.runtime.executors.sktime.executor import SktimeExecutor
from fomo.types.models import ModelInfo


def test_available_executors():
    names = available_executors()

    assert "sktime" in names
    assert "pytorch-forecasting" in names


def test_create_executor():
    executor = create_executor("sktime")

    assert isinstance(executor, SktimeExecutor)


def test_register():
    @register("test-executor")
    class DummyExecutor(Executor):
        def load(self, info, model):
            pass

        def warmup(self):
            pass

        def predict(self, request):
            pass

    assert isinstance(create_executor("test-executor"), DummyExecutor)


def test_create_executor_rejects_unknown():
    with pytest.raises(ValueError, match="unknown executor 'not-an-executor'"):
        create_executor("not-an-executor")


def test_pytorch_forecasting_executor():
    executor = create_executor("pytorch-forecasting")
    info = ModelInfo(id="pf", executor="pytorch-forecasting", source="registry")

    with pytest.raises(NotImplementedError, match="pytorch-forecasting"):
        executor.load(info, None)
