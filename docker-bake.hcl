# TServe images: same Dockerfile, different TSERVE_EXTRAS.
# Every tag is linux/amd64 + linux/arm64 (Linux, Mac, Windows Docker Desktop).
# `--extra gpu` is a torch index choice (PyPI / CUDA / MPS), not an arch pin.
#
# First time on a new machine:
#   docker run --privileged --rm tonistiigi/binfmt --install all
#   docker buildx create --name tserve --driver docker-container --bootstrap --use
#
# Build / Push / Load
#   docker buildx bake granite                         # build
#   docker buildx bake --push granite                  # build and push
#   docker buildx bake --set granite.platform=linux/amd64 --load granite
#   TSERVE_IMAGE=sktime/tserve docker buildx bake --push cpu
#   TSERVE_IMAGE=local/tserve docker buildx bake --load granite
#
# Groups:
#   default  base image
#   cpu      all CPU images
#   gpu      all GPU images

variable "TSERVE_IMAGE" {
  default = "sktime/tserve"
}

group "default" {
  targets = ["base"]
}

group "cpu" {
  targets = [
    "base", "hub", "chronos", "kronos", "granite",
    "moirai", "tirex", "toto", "mantis", "full",
  ]
}

group "gpu" {
  targets = [
    "hub-gpu", "chronos-gpu", "kronos-gpu", "granite-gpu",
    "moirai-gpu", "tirex-gpu", "toto-gpu", "mantis-gpu", "full-gpu",
  ]
}

target "_common" {
  context    = "."
  dockerfile = "Dockerfile"
  platforms  = ["linux/amd64", "linux/arm64"]
}

target "base" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "" }
  tags     = ["${TSERVE_IMAGE}:base"]
}

target "hub" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "hub" }
  tags     = ["${TSERVE_IMAGE}:hub"]
}

target "chronos" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "chronos" }
  tags     = ["${TSERVE_IMAGE}:chronos"]
}

target "kronos" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "kronos" }
  tags     = ["${TSERVE_IMAGE}:kronos"]
}

target "granite" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "granite" }
  tags     = ["${TSERVE_IMAGE}:granite"]
}

target "moirai" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "moirai" }
  tags     = ["${TSERVE_IMAGE}:moirai"]
}

target "tirex" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex" }
  tags     = ["${TSERVE_IMAGE}:tirex"]
}

target "toto" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "toto" }
  tags     = ["${TSERVE_IMAGE}:toto"]
}

target "mantis" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "mantis" }
  tags     = ["${TSERVE_IMAGE}:mantis"]
}

target "full" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "full" }
  tags     = ["${TSERVE_IMAGE}:full"]
}

target "hub-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "hub gpu" }
  tags     = ["${TSERVE_IMAGE}:hub-gpu"]
}

target "chronos-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "chronos gpu" }
  tags     = ["${TSERVE_IMAGE}:chronos-gpu"]
}

target "kronos-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "kronos gpu" }
  tags     = ["${TSERVE_IMAGE}:kronos-gpu"]
}

target "granite-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "granite gpu" }
  tags     = ["${TSERVE_IMAGE}:granite-gpu"]
}

target "moirai-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "moirai gpu" }
  tags     = ["${TSERVE_IMAGE}:moirai-gpu"]
}

target "tirex-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex gpu" }
  tags     = ["${TSERVE_IMAGE}:tirex-gpu"]
}

target "toto-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "toto gpu" }
  tags     = ["${TSERVE_IMAGE}:toto-gpu"]
}

target "mantis-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "mantis gpu" }
  tags     = ["${TSERVE_IMAGE}:mantis-gpu"]
}

target "full-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "full gpu" }
  tags     = ["${TSERVE_IMAGE}:full-gpu"]
}
