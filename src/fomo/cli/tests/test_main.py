from unittest.mock import MagicMock, patch

import pytest

from fomo import __version__
from fomo.cli.main import main


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


def test_main_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"fomo {__version__}"
