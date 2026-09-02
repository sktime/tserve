# Docker

Two images on Docker Hub:

| tag | extras | use |
| --- | --- | --- |
| [`geetu040/fomo:sktime`](https://hub.docker.com/r/geetu040/fomo) | `server` + `sktime-lite` + `sktime` | [registry](models.md) models |
| [`geetu040/fomo:base`](https://hub.docker.com/r/geetu040/fomo) | `server` + `sktime-lite` | `naive` only; tests and light workflows |

Both use the same entrypoint: `fomo serve --host 0.0.0.0 --port 8000`. The image `CMD` is `--load-models naive`. Extra `docker run` arguments **replace** that `CMD`.

## Run a published image

Registry models (`:sktime`):

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

Baseline only (`:base`):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:base
```

That last command loads `naive` from the image `CMD`. To load a different set, pass `--load-models` explicitly. `:base` cannot load Hub ids — those need `:sktime`.

Map the host port with `-p 8000:8000`. Inside the container the server already binds `0.0.0.0:8000`. `--gpus all` is recommended for Hub models.

## Mount a models directory

Saved sktime `.zip` files on the host can be loaded with `--models-dir` if you bind-mount the folder:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/my-models:/models" \
  geetu040/fomo:sktime \
  --models-dir /models \
  --load-models custom-model-1 custom-model-2
```

`$PWD/my-models` is the host directory; `/models` is the path inside the container. Only stems named in `--load-models` are loaded — the directory is not ingested wholesale. Mix zip stems with registry ids if you want both.

First load of a Hub id still downloads weights into the container. Mount a Hugging Face cache if you want them to survive `docker run --rm`:

```bash
docker run --rm --gpus all -p 8000:8000 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  geetu040/fomo:sktime \
  --load-models chronos-2 timesfm-2.5 ttm-r3-52-16
```

## Build from this repo

The [`Dockerfile`](https://github.com/sktime/fomo/blob/main/Dockerfile) always installs `server` and `sktime-lite`. Add Hub deps at build time:

```bash
git clone git@github.com:sktime/fomo.git && cd fomo

docker build -t fomo:base .
docker run --rm -p 8000:8000 fomo:base

docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
docker run --rm --gpus all -p 8000:8000 fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16
```

`FOMO_EXTRAS` is a space-separated list of extras, forwarded as `uv sync --extra …`. Same extras as [server dependencies](server.md#dependencies).

## Custom image

Add Python deps on top of a published image:

```dockerfile
FROM geetu040/fomo:sktime

RUN pip install my-package another-package
```

```bash
docker build -t my-fomo:custom .
docker run --rm -p 8000:8000 my-fomo:custom \
  --load-models naive chronos-2 timesfm-2.5
```

## Sidecar

Run FoMo next to an app that only needs the [client](client.md) extra:

```bash
docker run --rm --name fomo --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

From another container on the same network, `Client("http://fomo:8000")` or `curl http://fomo:8000/forecast`.
