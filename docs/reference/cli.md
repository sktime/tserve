# CLI

`fomo` has one subcommand, `serve`. [`main`][fomo.cli.main.main] parses argv, constructs [`Server`][fomo.server.serve.Server], and calls [`run`][fomo.server.serve.Server.run]. Returns `0` on normal exit and on `KeyboardInterrupt`. `parser.error` / argparse usage errors exit via `SystemExit`.

```bash
fomo serve \
  --load-models naive \
  --host 127.0.0.1 \
  --port 8000 \
  --log-level info
```

| flag | default | |
| --- | --- | --- |
| `--load-models` | none (`[]`) | registry ids to load; `nargs="+"` |
| `--models-dir` | none | directory scanned for stem rewrite; does **not** auto-load the directory |
| `--host` | `127.0.0.1` | bind address |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | uvicorn log level |

`--load-models` takes CLI names only. In-process `(id, estimator)` pairs are SDK-only. `--models-dir` rewrites matching **`.zip` stems** already named in `--load-models`; see [Load models](../how-to/load-models.md).

Omitting `--load-models` starts empty. Unknown registry ids, non-zip paths, missing executor extras, and duplicate ids fail during [`Server`][fomo.server.serve.Server] construction (before uvicorn starts).

```bash
fomo serve --help
fomo serve serve --help   # argparse: the subcommand is `serve`
```

The console script is `fomo = fomo.cli.main:main`.
