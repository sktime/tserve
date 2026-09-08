# CLI

`fomo` has one subcommand, `serve`. It constructs [`Server`][fomo.server.serve.Server] and calls `run`. Returns `0` on a normal exit and on `KeyboardInterrupt`.

## Usage

```bash
fomo serve --load-models chronos-bolt-tiny timesfm-2.5 --host 127.0.0.1 --port 8000 --log-level info
```

## Flags

| flag | default | |
| --- | --- | --- |
| `--load-models` | none | registry ids to load |
| `--models-dir` | none | rewrite matching `.zip` stems already named in `--load-models` |
| `--host` | `127.0.0.1` | bind address; use `0.0.0.0` in Docker |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | uvicorn log level |

`--load-models` takes names only. In-process `(id, estimator)` pairs are SDK-only. Omitting `--load-models` starts empty. Unknown registry ids fail during construction, before uvicorn starts.

```bash
fomo serve --help
```

Walkthrough: [running from source](../server/source.md).
