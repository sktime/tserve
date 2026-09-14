from unittest.mock import MagicMock, patch

import pytest

from fomo import __version__
from fomo.cli.main import main, parse_load_models


def _run(argv):
    server = MagicMock()
    with patch("fomo.server.Server", return_value=server) as Server:
        code = main(argv)
    return code, Server, server


def test_main():
    code, Server, server = _run(["serve"])

    assert code == 0
    Server.assert_called_once_with(
        load_models=[],
        models_dir=None,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server.run.assert_called_once()


def test_main_forwards_flags():
    _, Server, _ = _run(
        [
            "serve",
            "--load-models",
            "naive",
            "chronos-2",
            "--models-dir",
            "/models",
            "--host",
            "0.0.0.0",
            "--port",
            "9000",
            "--log-level",
            "debug",
        ]
    )

    Server.assert_called_once_with(
        load_models=["naive", "chronos-2"],
        models_dir="/models",
        host="0.0.0.0",
        port=9000,
        log_level="debug",
    )


def test_main_parses_craft_token():
    _, Server, _ = _run(
        [
            "serve",
            "--load-models",
            "naive",
            'drift=NaiveForecaster(strategy="drift")',
        ]
    )

    Server.assert_called_once_with(
        load_models=["naive", ("drift", 'NaiveForecaster(strategy="drift")')],
        models_dir=None,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )


def test_parse_load_models():
    assert parse_load_models(["naive", "chronos-2"]) == ["naive", "chronos-2"]
    assert parse_load_models(
        ['ttm-local=TinyTimeMixerForecaster(model_path="x", revision="a=b")']
    ) == [("ttm-local", 'TinyTimeMixerForecaster(model_path="x", revision="a=b")')]


@pytest.mark.parametrize(
    ("tokens", "match"),
    [
        pytest.param(["NaiveForecaster()"], "id=spec", id="bare_spec"),
        pytest.param(["=NaiveForecaster()"], "empty id", id="empty_id"),
        pytest.param(["mine="], "empty craft spec", id="empty_spec"),
    ],
)
def test_parse_load_models_rejects(tokens, match):
    with pytest.raises(ValueError, match=match):
        parse_load_models(tokens)


def test_main_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"fomo {__version__}"
