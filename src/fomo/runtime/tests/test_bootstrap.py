from unittest.mock import MagicMock, patch

import pytest

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.types.models import ModelInfo, ModelsResult


def _info(**kwargs):
    payload = {"id": "naive", "executor": "sktime", "source": "registry"}
    payload.update(kwargs)
    return ModelInfo.model_validate(payload)


def _executor():
    executor = MagicMock()
    executor.load_s = 1.24
    executor.warmup_s = 0.31
    return executor


def test_bootstrap():
    info = _info()
    executor = _executor()

    with (
        patch("fomo.runtime.bootstrap.resolve_model", return_value=info) as resolve_model,
        patch("fomo.runtime.bootstrap.create_executor", return_value=executor) as create_executor,
    ):
        runtime = bootstrap(["naive"])

    resolve_model.assert_called_once_with("naive")
    create_executor.assert_called_once_with("sktime")
    executor.load.assert_called_once_with(info, "naive")
    assert runtime.executors == {"naive": executor}
    assert runtime.models == {"naive": info}
    assert runtime.stats.snapshot()["models"]["naive"]["executor"] == "sktime"


def test_bootstrap_loads_object():
    info = _info(source="object")
    executor = _executor()
    model = object()

    with (
        patch("fomo.runtime.bootstrap.resolve_model", return_value=info),
        patch("fomo.runtime.bootstrap.create_executor", return_value=executor),
    ):
        bootstrap([("mine", model)])

    executor.load.assert_called_once_with(info, model)


def test_bootstrap_rejects_duplicate():
    with (
        patch("fomo.runtime.bootstrap.resolve_model", return_value=_info()),
        patch("fomo.runtime.bootstrap.create_executor", return_value=_executor()),
    ):
        with pytest.raises(ValueError, match="duplicate model id 'naive'"):
            bootstrap(["naive", "naive"])


def test_loaded_models():
    info = _info()
    runtime = Runtime(executors={}, scheduler=MagicMock(), models={"naive": info})

    assert runtime.loaded_models() == ModelsResult(models=[info])
