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
docker run --rm -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2
```

GPU (Hub models):

```bash
docker run --rm --gpus all -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2 timesfm-2.5 ttm-r3-52-16 toto-2.0-4m mantis-8m
```

Baseline only (`:base`):

```bash
docker run --rm -p 8000:8000 geetu040/fomo:base
```

That last command loads `naive` from the image `CMD`. To load a different set, pass `--load-models` explicitly. `:base` cannot load Hub ids — those need `:sktime`.

Map the host port with `-p 8000:8000`. Inside the container the server already binds `0.0.0.0:8000`.

## Build from this repo

The [`Dockerfile`](https://github.com/sktime/fomo/blob/main/Dockerfile) always installs `server` and `sktime-lite`. Add Hub deps at build time:

```bash
git clone git@github.com:sktime/fomo.git && cd fomo

docker build -t fomo:base .
docker run --rm -p 8000:8000 fomo:base

docker build --build-arg FOMO_EXTRAS=sktime -t fomo:sktime .
docker run --rm -p 8000:8000 fomo:sktime --load-models naive chronos-2
```

`FOMO_EXTRAS` is a space-separated list of extras, forwarded as `uv sync --extra …`.

## Custom image

Add Python deps on top of a published image:

```dockerfile
FROM geetu040/fomo:sktime

RUN pip install my-package another-package
```

```bash
docker build -t my-fomo:custom .
docker run --rm -p 8000:8000 my-fomo:custom \
  --load-models naive
```

## Sidecar

Run FoMo next to an app that only needs the [client](client.md) extra:

```bash
docker run --rm --name fomo -p 8000:8000 geetu040/fomo:sktime \
  --load-models naive chronos-2
```

From another container on the same network, `Client("http://fomo:8000")` or `curl http://fomo:8000/forecast`.

First load of a Hub id still downloads weights into the container. Mount a Hugging Face cache if you want them to survive `docker run --rm`.
