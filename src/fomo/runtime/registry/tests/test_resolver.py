from pathlib import Path

import pytest
from sktime.forecasting.naive import NaiveForecaster

from fomo.runtime.registry.resolver import resolve_model
from fomo.types.models import ModelInfo


def test_resolve_model_from_registry():
    info = resolve_model("naive")

    assert info == ModelInfo(id="naive", executor="sktime", source="registry")


def test_resolve_model_from_path(tmp_path):
    info = resolve_model(tmp_path / "naive.zip")

    assert info == ModelInfo(id="naive", executor="sktime", source="directory")


def test_resolve_model_from_object():
    info = resolve_model(("mine", NaiveForecaster()))

    assert info == ModelInfo(id="mine", executor="sktime", source="object")


@pytest.mark.parametrize(
    ("item", "exc", "match"),
    [
        pytest.param(
            "not-a-model",
            ValueError,
            "unknown registry 'not-a-model'",
            id="unknown_registry",
        ),
        pytest.param(
            Path("naive.pkl"),
            ValueError,
            "unknown file",
            id="non_zip_path",
        ),
        pytest.param(
            ("mine", object()),
            TypeError,
            "expected sktime object, got object",
            id="non_sktime_object",
        ),
    ],
)
def test_resolve_model_rejects(item, exc, match):
    with pytest.raises(exc, match=match):
        resolve_model(item)
