from unittest.mock import MagicMock, patch

import pytest

from fomo.runtime.bootstrap import Runtime, bootstrap
from fomo.types.models import ModelInfo, ModelsResult


def _info(**kwargs):
    payload = {"id": "naive", "executor": "sktime", "source": "registry"}
    payload.update(kwargs)
    return ModelInfo.model_validate(payload)


def _executor():
    return MagicMock()


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
    executor.warmup.assert_called_once_with()
    assert runtime.executors == {"naive": executor}
    assert runtime.models == {"naive": info}
    row = runtime.stats.snapshot()["models"]["naive"]
    assert row["executor"] == "sktime"
    assert isinstance(row["load_s"], float)
    assert isinstance(row["warmup_s"], float)
    assert row["load_s"] >= 0
    assert row["warmup_s"] >= 0


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
    executor.warmup.assert_called_once_with()


def test_bootstrap_rejects_duplicate():
    with (
        patch("fomo.runtime.bootstrap.resolve_model", return_value=_info()),
        patch("fomo.runtime.bootstrap.create_executor", return_value=_executor()),
    ):
        with pytest.raises(ValueError, match="duplicate model id 'naive' in load_models"):
            bootstrap(["naive", "naive"])


def test_loaded_models():
    info = _info()
    runtime = Runtime(executors={}, scheduler=MagicMock(), models={"naive": info})

    assert runtime.loaded_models() == ModelsResult(models=[info])
