from pathlib import Path

import pytest
from sktime.forecasting.naive import NaiveForecaster

from tserve.runtime.registry.resolver import resolve_model
from tserve.types.models import ModelInfo


def test_resolve_model_from_registry():
    info = resolve_model("naive")

    assert info == ModelInfo(id="naive", executor="sktime", source="registry")


def test_resolve_model_from_path(tmp_path):
    info = resolve_model(tmp_path / "naive.zip")

    assert info == ModelInfo(id="naive", executor="sktime", source="directory")


def test_resolve_model_from_object():
    info = resolve_model(("mine", NaiveForecaster()))

    assert info == ModelInfo(id="mine", executor="sktime", source="object")


def test_resolve_model_from_craft():
    info = resolve_model(("mine", "NaiveForecaster()"))

    assert info == ModelInfo(id="mine", executor="sktime", source="craft")


@pytest.mark.parametrize(
    ("item", "exc", "match"),
    [
        pytest.param(
            "not-a-model",
            ValueError,
            "unknown model 'not-a-model'",
            id="unknown_registry",
        ),
        pytest.param(
            "NaiveForecaster()",
            ValueError,
            "pass a \\(id, spec\\) pair",
            id="bare_craft_hint",
        ),
        pytest.param(
            Path("naive.pkl"),
            ValueError,
            "not a saved sktime model",
            id="non_zip_path",
        ),
        pytest.param(
            ("mine", object()),
            TypeError,
            "must be a sktime forecaster or a craft spec string, got object",
            id="non_sktime_object",
        ),
        pytest.param(
            ("mine", ""),
            ValueError,
            "empty craft spec",
            id="empty_craft",
        ),
        pytest.param(
            ("mine", "   "),
            ValueError,
            "empty craft spec",
            id="whitespace_craft",
        ),
    ],
)
def test_resolve_model_rejects(item, exc, match):
    with pytest.raises(exc, match=match):
        resolve_model(item)
