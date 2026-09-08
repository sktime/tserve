# Docker

Published images live at [`geetu040/fomo`](https://hub.docker.com/r/geetu040/fomo). Each tag is the same [`Dockerfile`](https://github.com/sktime/fomo/blob/main/Dockerfile) with a different `FOMO_EXTRAS` set. Tags are multi-arch (`linux/amd64` and `linux/arm64`) so Linux, macOS, and Windows Docker Desktop can pull them.

Both the CPU and GPU images use the same entrypoint: `fomo serve --host 0.0.0.0 --port 8000`. The image `CMD` is `--load-models naive`. Extra `docker run` arguments **replace** that `CMD`.

| tag | extras | families it can load |
| --- | --- | --- |
| `base` | `server` + `sktime` | `NaiveForecaster` |
| `hub` | `base` + `hub` | TTM, TimesFM 2.x, Chronos Bolt/T5 |
| `chronos` | `hub` + `chronos` | Chronos-2 |
| `granite` | `hub` + `granite` | FlowState |
| `moirai` | `hub` + `moirai` | Moirai, Lag-Llama |
| `tirex` | `hub` + `tirex` | TiRex |
| `toto` | `hub` + `toto` | Toto-2 |
| `mantis` | `hub` + `mantis` | Mantis |
| `kronos` | `base` + `kronos` | Kronos, WindFM (not the `hub` stack) |
| `full` | all family extras | every catalog family |
| `hub-gpu`, `chronos-gpu`, …, `full-gpu` | same extras + `gpu` | same families, CUDA/MPS torch |

There is no `base-gpu`. `kronos` does not include the `hub` extra.

## Run a published image

Hub models (CPU):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

Baseline only (`:base` loads `naive` from the image `CMD`):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:base
```

GPU (needs the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)):

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:hub-gpu --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

`:base` cannot load Hub ids — those need `:hub` or a family/`full` tag. Map the host port with `-p 8000:8000`. Inside the container the server already binds `0.0.0.0:8000`.

## Hugging Face token and cache

First load of a Hub id downloads weights into the container. Unauthenticated Hub traffic is rate-limited; the process logs a warning if `HF_TOKEN` is unset. A read token is enough:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN geetu040/fomo:hub --load-models chronos-bolt-tiny ttm-r3-512-30
```

Mount the host Hugging Face cache so checkpoints survive `docker run --rm`:

```bash
docker run --rm -p 8000:8000 -e HF_TOKEN -v "$HOME/.cache/huggingface:/root/.cache/huggingface" geetu040/fomo:hub --load-models chronos-bolt-tiny ttm-r3-512-30
```

## Mount a models directory

Saved sktime `.zip` files on the host can be loaded with `--models-dir` if you bind-mount the folder:

```bash
docker run --rm -p 8000:8000 -v "$PWD/my-models:/models" geetu040/fomo:hub --models-dir /models --load-models custom-model-1 custom-model-2
```

`$PWD/my-models` is the host directory; `/models` is the path inside the container. Only stems named in `--load-models` are loaded — the directory is not ingested wholesale. Mix zip stems with registry ids if you want both.

## Build from this repo

[`docker-bake.hcl`](https://github.com/sktime/fomo/blob/main/docker-bake.hcl) is the build matrix. The Dockerfile always installs `server` and `sktime`. Bake adds family extras.

```bash
git clone https://github.com/sktime/fomo.git && cd fomo
```

Load a single tag into the local daemon (one platform):

```bash
FOMO_IMAGE=fomo docker buildx bake --set base.platform=linux/amd64 --load base
docker run --rm -p 8000:8000 fomo:base
```

Or a plain `docker build` (same `FOMO_EXTRAS` knob):

```bash
docker build -t fomo:base .
docker build --build-arg FOMO_EXTRAS=hub -t fomo:hub .
docker build --build-arg FOMO_EXTRAS="hub gpu" -t fomo:hub-gpu .
```

`FOMO_EXTRAS` is a space-separated list of extras, forwarded as `uv sync --extra …`. Same extras as [server dependencies](index.md#dependencies).

Push the published namespace (default bake image is `sktime/fomo`; override to match Docker Hub):

```bash
FOMO_IMAGE=geetu040/fomo docker buildx bake --push hub
FOMO_IMAGE=geetu040/fomo docker buildx bake --push cpu
FOMO_IMAGE=geetu040/fomo docker buildx bake --push gpu
```

Groups: `default` → `base`; `cpu` → every CPU tag; `gpu` → every `*-gpu` tag.

First time on a new machine, install binfmt and a buildx builder before a multi-arch bake:

```bash
docker run --privileged --rm tonistiigi/binfmt --install all
docker buildx create --name fomo --driver docker-container --bootstrap --use
```

## Custom image

Add Python deps on top of a published image:

```dockerfile
FROM geetu040/fomo:hub

RUN pip install my-package another-package
```

```bash
docker build -t my-fomo:custom .
docker run --rm -p 8000:8000 my-fomo:custom --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

## Sidecar

Run FoMo next to an app that only needs the [Python client](../client/python.md) extra:

```bash
docker run --rm --name fomo -p 8000:8000 geetu040/fomo:hub --load-models naive chronos-bolt-tiny ttm-r3-512-30
```

From another container on the same network, `Client("http://fomo:8000")` or `curl http://fomo:8000/forecast`.
