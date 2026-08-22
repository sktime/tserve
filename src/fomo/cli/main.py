import argparse


def _build_parser() -> argparse.ArgumentParser:
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
