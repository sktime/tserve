from __future__ import annotations

import argparse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fomo")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="run the inference server")
    serve.add_argument(
        "--load-model",
        nargs="+",
        dest="load_model",
        default=None,
        help="model aliases to load (default: dummy chronos2 timesfm2.5 moirai2 kronos)",
    )
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--log-level", default="info", dest="log_level")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "serve":
        parser.error(f"unknown command {args.command}")

    from fomo.server import Server

    server = Server(
        load_model=args.load_model,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )
    try:
        server.run()
    except KeyboardInterrupt:
        return 0
    return 0
