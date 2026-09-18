"""argparse CLI for ``fomo serve``.

Builds a ``Server`` from flags and calls ``run``. Returns 0 on
normal exit and on ``KeyboardInterrupt``.
"""

import argparse
from pathlib import Path
from typing import Any

from fomo import __version__


def parse_model(tokens: list[str]) -> list[str | Path | tuple[str, Any]]:
    """Turn ``--model`` and leftover positional tokens into ``Server`` ``model`` items.

    A token without ``=`` is a registry id (or ``--models-dir`` stem).
    A token with ``=`` is split on the first ``=`` into ``(id, spec)``.
    Specs may contain further ``=`` (constructor kwargs).

    Parameters
    ----------
    tokens : list of str
        Raw ``--model`` values and leftover positional ids.

    Returns
    -------
    list of str or (str, str)
        Registry ids and craft ``(id, spec)`` pairs.

    Raises
    ------
    ValueError
        Empty id or spec after ``=``, or a token that looks like a
        craft spec but has no ``id=`` prefix.
    """
    items: list[str | Path | tuple[str, Any]] = []
    for token in tokens:
        if "=" not in token:
            if "(" in token:
                raise ValueError(
                    f"unknown model {token!r}; wrap a craft spec as id=spec,"
                    " e.g. 'my-model=NaiveForecaster()'."
                )
            items.append(token)
            continue

        model_id, spec = token.split("=", 1)
        model_id = model_id.strip()
        spec = spec.strip()
        if not model_id:
            raise ValueError("model craft entry has an empty id")
        if not spec:
            raise ValueError(f"model entry {model_id!r} has an empty craft spec")
        items.append((model_id, spec))
    return items


def _build_parser() -> argparse.ArgumentParser:
    """Build the ``fomo`` parser with a required ``serve`` subcommand.

    ``serve`` flags: ``--model`` (``nargs="+"``, default ``[]``;
    extra catalog ids or ``id=spec`` craft tokens; ``naive`` is always
    loaded), leftover positional ids (same meaning as ``--model``),
    ``--models-dir`` (rewrites matching stems to paths; does not
    auto-load the directory), ``--host`` (default ``127.0.0.1``),
    ``--port`` (default 8000), ``--log-level`` (default ``info``;
    ``debug``, ``info``, ``warning``, ``error``, or ``critical``).

    Returns
    -------
    argparse.ArgumentParser
        Parser with ``prog="fomo"`` and required dest ``command``.
    """
    parser = argparse.ArgumentParser(prog="fomo", allow_abbrev=False)
    parser.add_argument(
        "--version",
        action="version",
        version=f"fomo {__version__}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="run the inference server", allow_abbrev=False)
    serve.add_argument(
        "--model",
        nargs="+",
        dest="model",
        default=[],
        help="extra registry ids or id=craft-spec to load (naive is always loaded)",
    )
    serve.add_argument(
        "--models-dir",
        dest="models_dir",
        default=None,
        help="directory of models to load (default: none)",
    )
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument(
        "--log-level",
        default="info",
        dest="log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="FoMo and uvicorn verbosity (default: info)",
    )
    serve.add_argument(
        "positional_model",
        nargs="*",
        metavar="MODEL",
        help="extra registry ids or id=craft-spec; same as --model",
    )
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
        If ``--model`` or positional tokens are malformed (empty ``id=spec``,
        a bare craft spec), or ``Server`` / ``bootstrap`` reject a
        load spec (duplicate id, unknown registry id, non-zip path,
        unknown executor).
    TypeError
        If a model object is not a sktime ``BaseForecaster``.
    ImportError
        If the executor extra is not installed.

    See Also
    --------
    fomo.server.serve.Server
        Constructed from ``--model`` / leftover positionals, ``--models-dir``,
        ``--host``, ``--port``, and ``--log-level``.
    [Install and serve](../server/index.md)
        Install server and model-family dependencies.
    [Models catalog](../models/index.md)
        Registry ids accepted by ``--model`` or leftover positionals.
    [Docker](../server/docker.md)
        Container entrypoint.
    [Startup errors](../reference/errors.md#startup)
        Failures that occur before uvicorn binds the port.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "serve":
        parser.error(f"unknown command {args.command}")

    from fomo.server import Server

    server = Server(
        model=parse_model([*args.model, *args.positional_model]),
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
