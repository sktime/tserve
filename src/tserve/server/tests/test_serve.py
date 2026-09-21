from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from tserve.server.serve import Server


def _server(**kwargs):
    runtime = MagicMock()
    with patch("tserve.server.serve.bootstrap", return_value=runtime) as bootstrap:
        server = Server(**kwargs)
    return server, bootstrap, runtime


def test_server():
    server, bootstrap, runtime = _server(model=["naive"])

    assert isinstance(server.app, FastAPI)
    assert server.app.state.runtime is runtime
    bootstrap.assert_called_once_with(["naive"])
    assert server.url == "http://127.0.0.1:8000"


def test_server_loads_naive_by_default():
    _, bootstrap, _ = _server()

    bootstrap.assert_called_once_with(["naive"])


def test_server_prepends_naive():
    _, bootstrap, _ = _server(model=["chronos_2"])

    bootstrap.assert_called_once_with(["naive", "chronos_2"])


def test_server_does_not_duplicate_naive():
    _, bootstrap, _ = _server(model=["naive", "chronos_2"])

    bootstrap.assert_called_once_with(["naive", "chronos_2"])


def test_server_does_not_duplicate_naive_craft():
    spec = 'NaiveForecaster(strategy="drift")'
    _, bootstrap, _ = _server(model=[("naive", spec)])

    bootstrap.assert_called_once_with([("naive", spec)])


def test_server_uses_models_dir(tmp_path):
    model_path = tmp_path / "naive.zip"
    model_path.write_bytes(b"")

    _, bootstrap, _ = _server(model=["naive"], models_dir=tmp_path)

    bootstrap.assert_called_once_with([model_path])


def test_run():
    server, _, _ = _server()

    with patch("tserve.server.serve.uvicorn.run") as run:
        server.run()

    run.assert_called_once_with(
        server.app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
