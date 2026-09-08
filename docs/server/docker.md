# Docker

Images ship Python, the FoMo package, and one set of model dependencies. The tag decides which model families the process can load; the arguments decide which ids it actually loads.

## Pull an image

```bash
docker pull geetu040/fomo:hub
```

`base` carries `naive` only. `hub` adds Chronos Bolt/T5, TTM, and TimesFM 2.x. Family tags (`chronos`, `granite`, `kronos`, `moirai`, `tirex`, `toto`, `mantis`) each add one more stack, `full` has all of them, and every family tag has a `*-gpu` variant. The tag-to-ids map lives on [Load models](../models/index.md).

Tags are published for `linux/amd64` and `linux/arm64`, so Docker Desktop on macOS and Windows uses the same commands as Linux.

## Run the server

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models chronos-bolt-tiny timesfm-2.5
```

Anything after the image name replaces the image `CMD`, which is `--load-models naive`. So `docker run --rm -p 8000:8000 geetu040/fomo:hub` serves `naive` — that default belongs to the image, not to `fomo serve`.

The `ENTRYPOINT` already passes `--host 0.0.0.0 --port 8000`. Leave the container port alone and remap the host side if 8000 is taken:

```bash
docker run --rm -p 9000:8000 geetu040/fomo:hub --load-models chronos-bolt-tiny
```

The container logs `http://0.0.0.0:8000`; from the host, open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (or `9000` in the example above). `docker run` without `--rm` keeps the stopped container around, which is worth it when you want `docker logs` after a crash.

## Choose which models to load

Ids must belong to the families baked into the tag: `chronos-bolt-tiny` and `timesfm-2.5` need `:hub` or `:full`, while `chronos-2` needs `:chronos`. An unknown id fails immediately with the known ids listed; an id whose family is missing from the image fails when that model loads.

`naive` downloads nothing. Every other id fetches a checkpoint from Hugging Face on first load, which is why the [token](#hugging-face-token) and [cache mount](#keep-weights-between-runs) below are worth setting. Start with [Load models](../models/index.md), and see the [catalog](../models/catalog.md) for every id.

## Hugging Face token

Unauthenticated Hugging Face downloads are rate-limited. A read token avoids that; `-e HF_TOKEN` forwards the value from your own environment:

=== "bash / zsh"

    ```bash
    export HF_TOKEN=hf_your_token
    docker run --rm -p 8000:8000 -e HF_TOKEN geetu040/fomo:hub --load-models chronos-bolt-tiny
    ```

=== "PowerShell"

    ```powershell
    $env:HF_TOKEN = "hf_your_token"
    docker run --rm -p 8000:8000 -e HF_TOKEN geetu040/fomo:hub --load-models chronos-bolt-tiny
    ```

## Keep weights between runs

The container caches checkpoints in `/root/.cache/huggingface`, which disappears with the container. Mount your host cache so a restart reuses the download:

=== "bash / zsh"

    ```bash
    docker run --rm -p 8000:8000 -v "$HOME/.cache/huggingface:/root/.cache/huggingface" geetu040/fomo:hub --load-models chronos-bolt-tiny timesfm-2.5
    ```

=== "PowerShell"

    ```powershell
    docker run --rm -p 8000:8000 -v "${env:USERPROFILE}\.cache\huggingface:/root/.cache/huggingface" geetu040/fomo:hub --load-models chronos-bolt-tiny timesfm-2.5
    ```

A named volume works too (`-v fomo-hf:/root/.cache/huggingface`) if you would rather not share the host cache.

## GPU images

The `*-gpu` tags install torch from PyPI instead of the CPU wheel index. They need an NVIDIA GPU, the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) on the host, and `--gpus all` on the command:

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:hub-gpu --load-models chronos-bolt-tiny timesfm-2.5
```

That covers Linux and Windows through WSL2. Docker on macOS has no GPU passthrough, so Apple silicon acceleration means [installing from source](source.md) with the `gpu` extra, which resolves to MPS-capable torch.

## Models from a directory

Mount the directory and point `--models-dir` at the container path:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" geetu040/fomo:hub --models-dir /models --load-models custom-model-1 chronos-bolt-tiny
```

Only stems you also name in `--load-models` are loaded from disk — the rules are on [Models from a directory](models-dir.md).

## Dashboard

The dashboard is part of the app, so there is nothing extra to enable; the `-p` mapping is what makes it reachable. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/), and see [Dashboard](dashboard.md) for what it can do.

## Build an image yourself

The [Dockerfile](https://github.com/sktime/fomo/blob/main/Dockerfile) always installs `--extra server --extra sktime`; `FOMO_EXTRAS` adds the heavier ones:

```bash
docker build --build-arg FOMO_EXTRAS=hub -t fomo:hub .
```

Several extras go in one quoted argument:

```bash
docker build --build-arg FOMO_EXTRAS="chronos gpu" -t fomo:chronos-gpu .
```

`docker-bake.hcl` holds the published matrix — one target per tag, plus `cpu` and `gpu` groups. `FOMO_IMAGE` sets the image name:

```bash
FOMO_IMAGE=local/fomo docker buildx bake --set hub.platform=linux/amd64 --load hub
```

Bake targets are multi-platform by default, so a plain `docker buildx bake hub` needs a container builder (and `--push`, since multi-platform results cannot land in the local image store). Details are in [Development](../reference/development.md#docker-images).
