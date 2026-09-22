# Docker

The image tag chooses which families can load. Arguments after the image name choose which models do load. `naive` always loads.

## Pull an image

```bash
docker pull sktime/tserve:hub
```

Tags, families, and an example model are on [Dependencies](../models/index.md#dependencies). `hub` is Chronos Bolt/T5, TTM, and TimesFM. `chronos`, `granite`, `moirai`, `tirex`, `toto`, and `mantis` include Hub plus one more stack. `kronos` is built on `base`, not `hub`. `full` has every family. Each of those has a `*-gpu` tag. There is no `:base-gpu`.

Tags are published for `linux/amd64` and `linux/arm64`, so Docker Desktop on macOS and Windows uses the same commands as Linux.

## Run the server

The image `ENTRYPOINT` is `tserve --host 0.0.0.0 --port 8000`. Anything after the image name is passed to that command: model names (`chronos_bolt ttm_r3`) and any [CLI](../reference/cli.md) flag (`--models-dir`, `--log-level`, `--host`, `--port`). Flags: [UV / Pip](pip.md#serve-from-the-command-line). Quote craft tokens the same way as on the host: [Craft specs](craft-specs.md).

```bash
docker run --rm -p 8000:8000 sktime/tserve:hub chronos_bolt ttm_r3
```

Leave the container port at 8000 and remap the host side if that port is taken:

```bash
docker run --rm -p 9000:8000 sktime/tserve:hub chronos_bolt
```

The container logs `http://0.0.0.0:8000`; from the host, open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (or `9000` in the example above). `docker run` without `--rm` keeps the stopped container around, which is worth it when you want `docker logs` after a crash.

## Choose which models to load

Models must belong to the families baked into the tag. `chronos_bolt` and `ttm_r3` load on `:hub` or `:full`. `chronos_2` loads on `:chronos` or `:full`. An unknown model fails immediately with the known models listed; a model whose family is missing from the image fails when that model loads.

`:moirai` carries Moirai 2, Moirai 1.x, and Lag-Llama, so `moirai_2` loads there and not on `:hub`:

```bash
docker run --rm -p 8000:8000 sktime/tserve:moirai moirai_2
```

When the models span more than one family, `:full` is the tag that carries all of them:

```bash
docker run --rm -p 8000:8000 sktime/tserve:full moirai_2 tirex
```

`naive` downloads nothing. Every other model fetches a checkpoint on first load, so set the [token](#hugging-face-token) and [cache mount](#keep-weights-between-runs) below. All 110 models: [catalog](../models/index.md).

## Hugging Face token

Unauthenticated Hugging Face downloads are rate-limited. A read token avoids that; `-e HF_TOKEN` forwards the value from your own environment:

=== "bash / zsh"

    ```bash
    export HF_TOKEN=hf_your_token
    docker run --rm -p 8000:8000 -e HF_TOKEN sktime/tserve:hub chronos_bolt
    ```

=== "PowerShell"

    ```powershell
    $env:HF_TOKEN = "hf_your_token"
    docker run --rm -p 8000:8000 -e HF_TOKEN sktime/tserve:hub chronos_bolt
    ```

## Keep weights between runs

The container caches checkpoints in `/root/.cache/huggingface`, which disappears with the container. Mount your host cache so a restart reuses the download:

=== "bash / zsh"

    ```bash
    docker run --rm -p 8000:8000 -v "$HOME/.cache/huggingface:/root/.cache/huggingface" sktime/tserve:hub chronos_bolt ttm_r3
    ```

=== "PowerShell"

    ```powershell
    docker run --rm -p 8000:8000 -v "${env:USERPROFILE}\.cache\huggingface:/root/.cache/huggingface" sktime/tserve:hub chronos_bolt ttm_r3
    ```

A named volume works too (`-v tserve-hf:/root/.cache/huggingface`) if you would rather not share the host cache.

## GPU images

The `*-gpu` tags install torch from PyPI instead of the CPU wheel index. They need an NVIDIA GPU, the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) on the host, and `--gpus all` on the command:

```bash
docker run --rm --gpus all -p 8000:8000 sktime/tserve:hub-gpu chronos_bolt ttm_r3
```

That covers Linux and Windows through WSL2. Docker on macOS has no GPU passthrough, so Apple silicon acceleration means a [local UV / Pip install](pip.md#install), which takes the MPS build of torch.

## Models from a directory

Mount the directory and point `--models-dir` at the container path:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" sktime/tserve:hub --models-dir /models custom-model-1 chronos_bolt
```

Only stems you also name on the command line are loaded from disk. Rules: [Models from a directory](models-dir.md). The dashboard is already in the image; open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) ([Dashboard](dashboard.md)).

## Build an image yourself

The build context is the repository, so start from a clone:

```bash
git clone https://github.com/sktime/tserve.git
cd tserve
```

### One image with `docker build`

The [Dockerfile](https://github.com/sktime/tserve/blob/main/Dockerfile) always installs `--extra server --extra sktime`; `TSERVE_EXTRAS` adds the heavier ones:

```bash
docker build --build-arg TSERVE_EXTRAS=hub -t tserve:hub .
```

Several extras go in one quoted argument:

```bash
docker build --build-arg TSERVE_EXTRAS="chronos gpu" -t tserve:chronos-gpu .
```

This builds for the architecture of the machine you are on and leaves the image in the local store, which is all you need to run it locally:

```bash
docker run --rm -p 8000:8000 tserve:hub chronos_bolt
```

### Set up buildx

Published tags are `linux/amd64` and `linux/arm64`. A plain `docker build` cannot emit both. Check that [Buildx](https://docs.docker.com/build/) is installed:

```bash
docker buildx version
```

If that fails, follow the [Buildx installation guide](https://github.com/docker/buildx#installing). Once per machine, register QEMU and create a container builder (the default `docker` driver builds one platform at a time):

```bash
docker run --privileged --rm tonistiigi/binfmt --install all
docker buildx create --name tserve --driver docker-container --bootstrap --use
```

`docker buildx use default` switches back. Drivers and cross-builds: [builders](https://docs.docker.com/build/builders/), [multi-platform builds](https://docs.docker.com/build/building/multi-platform/).

### Bake the published matrix

[`docker-bake.hcl`](https://github.com/sktime/tserve/blob/main/docker-bake.hcl) has one target per tag (`base`, `hub`, the family tags, `full`, and every `*-gpu` variant), plus `cpu` and `gpu` groups. `TSERVE_IMAGE` defaults to `sktime/tserve`.

Multi-platform images cannot be loaded locally, so bake pushes them:

```bash
TSERVE_IMAGE=local/tserve docker buildx bake --push hub
TSERVE_IMAGE=local/tserve docker buildx bake --push cpu
```

One platform, kept on the machine:

```bash
TSERVE_IMAGE=local/tserve docker buildx bake --set hub.platform=linux/amd64 --load hub
```

Release builds: [Development](../reference/development.md#docker-images).
