# CLI

`tserve` builds [`Server`][tserve.server.serve.Server] and calls `run`, which blocks until the process stops.

```bash
tserve chronos_bolt ttm_r3
```

Names after `tserve` are models to load. `naive` is always loaded as well.

Startup output: [Docker](../server/docker.md), [UV / Pip](../server/pip.md#serve-from-the-command-line).

## Flags

| flag | default | |
| --- | --- | --- |
| `MODEL …` | none | catalog models and/or `id=craft-spec` tokens. `naive` is always loaded too |
| `--models-dir` | none | directory of saved sktime `.zip` files |
| `--host` | `127.0.0.1` | bind address; `0.0.0.0` also accepts connections from the network |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | `debug`, `info`, `warning`, `error`, or `critical`, for TServe and uvicorn |

A craft spec is `id=spec`, split on the first `=`, so constructor kwargs may contain `=` too. Quote the whole token:

```bash
tserve chronos_bolt \
  'ttm-local=TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
```

`--models-dir` never loads a directory wholesale. It loads `.zip` stems you also named; other names fall through to the registry. A live estimator has no CLI form: [Live objects](../server/live-objects.md). Quoting and `source` values: [Craft specs](../server/craft-specs.md).

## Startup and exit

Models load while `Server` is constructed, so an unknown model, a missing dependency, or a duplicate model fails before uvicorn binds the port. Those exceptions are listed under [Errors](errors.md#startup).

`Ctrl+C` and a normal server exit both return `0`; argparse usage errors exit `2`. `tserve --help` prints the flags above.

In Docker the entrypoint is already `tserve --host 0.0.0.0 --port 8000`. Arguments after the image name are models or flags, so `chronos_bolt ttm_r3` and any flag here work there too: [Docker](../server/docker.md).

## Python entry point

::: tserve.cli.main.main
    options:
      heading_level: 3
