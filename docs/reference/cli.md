# CLI

`fomo` has one subcommand. `fomo serve` builds
[`Server`][fomo.server.serve.Server] and calls `run`, which blocks until the
process stops.

```bash
fomo serve --load-models chronos-bolt timesfm-2.5
```

A walkthrough with the startup output is on
[From source](../server/source.md#serve-from-the-command-line).

## Flags

| flag | default | |
| --- | --- | --- |
| `--load-models` | none | one or more ids to load; nothing loads without it |
| `--models-dir` | none | directory of saved sktime `.zip` files |
| `--host` | `127.0.0.1` | bind address; `0.0.0.0` also accepts connections from the network |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | `debug`, `info`, `warning`, `error`, or `critical`, for FoMo and uvicorn |

`--load-models` takes ids only. `--models-dir` never loads a directory
wholesale: it rewrites the ids you already named when they match a `.zip` stem
in that directory, and the rest fall through to the registry. Serving an
estimator you built in Python has no CLI form — see
[Live objects](../server/live-objects.md).

## Startup and exit

Models load while `Server` is constructed, so an unknown id, a missing
dependency, or a duplicate id fails before uvicorn binds the port. Those
exceptions are listed under [Errors](errors.md#startup).

`Ctrl+C` and a normal server exit both return `0`; argparse usage errors exit
`2`. `fomo serve --help` prints the flags above.

In Docker the entrypoint is already `fomo serve --host 0.0.0.0 --port 8000`,
and the image `CMD` is `--load-models naive`. Arguments after the image name
replace that `CMD`, so every flag here works there too — see
[Docker](../server/docker.md).

## Python entry point

::: fomo.cli.main.main
    options:
      heading_level: 3
