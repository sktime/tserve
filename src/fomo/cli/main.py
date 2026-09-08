"""argparse CLI for ``fomo serve``.

Builds a ``Server`` from flags and calls ``run``. Returns 0 on
normal exit and on ``KeyboardInterrupt``.
"""

import argparse


def _build_parser() -> argparse.ArgumentParser:
    """Build the ``fomo`` parser with a required ``serve`` subcommand.

    ``serve`` flags: ``--load-models`` (``nargs="+"``, default ``[]``),
    ``--models-dir`` (rewrites matching stems to paths; does not
    auto-load the directory), ``--host`` (default ``127.0.0.1``),
    ``--port`` (default 8000), ``--log-level`` (default ``info``).

    Returns
    -------
    argparse.ArgumentParser
        Parser with ``prog="fomo"`` and required dest ``command``.
    """
    parser = argparse.ArgumentParser(prog="fomo")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="run the inference server")
    serve.add_argument(
        "--load-models",
        nargs="+",
        dest="load_models",
        default=[],
        help="registry ids to load (default: none)",
    )
    serve.add_argument(
        "--models-dir",
        dest="models_dir",
        default=None,
        help="directory of models to load (default: none)",
    )
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--log-level", default="info", dest="log_level")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv, construct ``Server``, and run it.

    Requires subcommand ``serve``. Unknown ``command`` values call
    ``parser.error`` (should not occur with the required subparser).
    ``KeyboardInterrupt`` from ``server.run`` returns 0.

    Parameters
    ----------
    argv : list of str, optional
        Arguments for ``parse_args``. ``None`` uses ``sys.argv``.

    Returns
    -------
    int
        Always ``0`` on return. ``parser.error`` exits via
        ``SystemExit`` instead of returning.

    Raises
    ------
    SystemExit
        From ``ArgumentParser.error`` or argparse usage errors.
    ValueError
        If ``Server`` / ``bootstrap`` reject a load spec (duplicate
        id, unknown registry id, non-zip path, unknown executor).
    TypeError
        If a load-models object is not a sktime ``BaseForecaster``.
    ImportError
        If the executor extra is not installed.

    See Also
    --------
    fomo.server.serve.Server
        Constructed from ``--load-models``, ``--models-dir``,
        ``--host``, ``--port``, and ``--log-level``.
    [Install and serve](../server/index.md)
        Install server and model-family dependencies.
    [Models catalog](../models/index.md)
        Registry ids accepted by ``--load-models``.
    [Docker](../server/docker.md)
        Container entrypoint and default ``--load-models naive`` CMD.
    [Startup errors](../reference/errors.md#startup)
        Failures that occur before uvicorn binds the port.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "serve":
        parser.error(f"unknown command {args.command}")

    from fomo.server import Server

    server = Server(
        load_models=args.load_models,
        models_dir=args.models_dir,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )
    try:
        server.run()
    except KeyboardInterrupt:
        return 0
    return 0
