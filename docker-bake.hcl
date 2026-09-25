# TServe images: same Dockerfile, different TSERVE_EXTRAS.
# Every tag is linux/amd64 + linux/arm64 (Linux, Mac, Windows Docker Desktop).
# Empty TSERVE_CPU keeps PyPI torch (CUDA on Linux). CPU tags set TSERVE_CPU
# so the CPU wheel is installed. There is no gpu extra. :base has no torch.
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
    "moirai", "tirex", "tirex2", "toto", "mantis", "timesfm3", "t0", "tafsut", "full",
  ]
}

group "gpu" {
  targets = [
    "hub-gpu", "chronos-gpu", "kronos-gpu", "granite-gpu",
    "moirai-gpu", "tirex-gpu", "tirex2-gpu", "toto-gpu", "mantis-gpu",
    "timesfm3-gpu", "t0-gpu", "tafsut-gpu", "full-gpu",
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
  args     = { TSERVE_EXTRAS = "hub", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:hub"]
}

target "chronos" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "chronos", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:chronos"]
}

target "kronos" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "kronos", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:kronos"]
}

target "granite" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "granite", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:granite"]
}

target "moirai" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "moirai", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:moirai"]
}

target "tirex" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:tirex"]
}

target "tirex2" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex2", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:tirex2"]
}

target "toto" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "toto", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:toto"]
}

target "mantis" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "mantis", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:mantis"]
}

target "timesfm3" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "timesfm3", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:timesfm3"]
}

target "t0" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "t0", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:t0"]
}

target "tafsut" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tafsut", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:tafsut"]
}

target "full" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "full", TSERVE_CPU = "1" }
  tags     = ["${TSERVE_IMAGE}:full"]
}

target "hub-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "hub" }
  tags     = ["${TSERVE_IMAGE}:hub-gpu"]
}

target "chronos-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "chronos" }
  tags     = ["${TSERVE_IMAGE}:chronos-gpu"]
}

target "kronos-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "kronos" }
  tags     = ["${TSERVE_IMAGE}:kronos-gpu"]
}

target "granite-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "granite" }
  tags     = ["${TSERVE_IMAGE}:granite-gpu"]
}

target "moirai-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "moirai" }
  tags     = ["${TSERVE_IMAGE}:moirai-gpu"]
}

target "tirex-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex" }
  tags     = ["${TSERVE_IMAGE}:tirex-gpu"]
}

target "tirex2-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tirex2" }
  tags     = ["${TSERVE_IMAGE}:tirex2-gpu"]
}

target "toto-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "toto" }
  tags     = ["${TSERVE_IMAGE}:toto-gpu"]
}

target "mantis-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "mantis" }
  tags     = ["${TSERVE_IMAGE}:mantis-gpu"]
}

target "timesfm3-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "timesfm3" }
  tags     = ["${TSERVE_IMAGE}:timesfm3-gpu"]
}

target "t0-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "t0" }
  tags     = ["${TSERVE_IMAGE}:t0-gpu"]
}

target "tafsut-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "tafsut" }
  tags     = ["${TSERVE_IMAGE}:tafsut-gpu"]
}

target "full-gpu" {
  inherits = ["_common"]
  args     = { TSERVE_EXTRAS = "full" }
  tags     = ["${TSERVE_IMAGE}:full-gpu"]
}
