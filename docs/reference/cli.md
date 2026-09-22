# CLI

`tserve` builds [`Server`][tserve.server.serve.Server] and calls `run`, which blocks until the process stops.

```bash
tserve chronos_bolt ttm_r3
```

Catalog models are leftover positionals after `tserve`. `naive` is always loaded as a test baseline.

A walkthrough with the startup output is on [Docker](../server/docker.md) and [UV / Pip](../server/pip.md#serve-from-the-command-line).

## Flags

| flag | default | |
| --- | --- | --- |
| `MODEL …` | none | extra catalog models and/or `id=craft-spec` tokens. `naive` is always loaded as a test baseline |
| `--models-dir` | none | directory of saved sktime `.zip` files |
| `--host` | `127.0.0.1` | bind address; `0.0.0.0` also accepts connections from the network |
| `--port` | `8000` | bind port |
| `--log-level` | `info` | `debug`, `info`, `warning`, `error`, or `critical`, for TServe and uvicorn |

Leftover positionals take catalog models, or craft specs as `id=spec` (split on the first `=`). Quote the whole token so constructor kwargs survive the shell:

```bash
tserve chronos_bolt \
  'ttm-local=TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r3", revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
```

`--models-dir` never loads a directory wholesale: it rewrites the models you already named when they match a `.zip` stem in that directory, and the rest fall through to the registry. Serving a live estimator you built in Python has no CLI form — see [Live objects](../server/live-objects.md). Craft specs are documented with quoting and `GET /models` source values on [Craft specs](../server/craft-specs.md).

## Startup and exit

Models load while `Server` is constructed, so an unknown model, a missing dependency, or a duplicate model fails before uvicorn binds the port. Those exceptions are listed under [Errors](errors.md#startup).

`Ctrl+C` and a normal server exit both return `0`; argparse usage errors exit `2`. `tserve --help` prints the flags above.

In Docker the entrypoint is already `tserve --host 0.0.0.0 --port 8000`. Arguments after the image name are extra models or flags, so leftover models (`chronos_bolt ttm_r3`) or any flag here work there too — see [Docker](../server/docker.md).

## Python entry point

::: tserve.cli.main.main
    options:
      heading_level: 3
