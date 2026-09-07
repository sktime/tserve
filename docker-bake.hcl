variable "FOMO_IMAGE" {
  default = "sktime/fomo"
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
  args     = { FOMO_EXTRAS = "" }
  tags     = ["${FOMO_IMAGE}:base"]
}

target "hub" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "hub" }
  tags     = ["${FOMO_IMAGE}:hub"]
}

target "chronos" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "chronos" }
  tags     = ["${FOMO_IMAGE}:chronos"]
}

target "kronos" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "kronos" }
  tags     = ["${FOMO_IMAGE}:kronos"]
}

target "granite" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "granite" }
  tags     = ["${FOMO_IMAGE}:granite"]
}

target "moirai" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "moirai" }
  tags     = ["${FOMO_IMAGE}:moirai"]
}

target "tirex" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "tirex" }
  tags     = ["${FOMO_IMAGE}:tirex"]
}

target "toto" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "toto" }
  tags     = ["${FOMO_IMAGE}:toto"]
}

target "mantis" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "mantis" }
  tags     = ["${FOMO_IMAGE}:mantis"]
}

target "full" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "full" }
  tags     = ["${FOMO_IMAGE}:full"]
}

target "hub-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "hub gpu" }
  tags     = ["${FOMO_IMAGE}:hub-gpu"]
}

target "chronos-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "chronos gpu" }
  tags     = ["${FOMO_IMAGE}:chronos-gpu"]
}

target "kronos-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "kronos gpu" }
  tags     = ["${FOMO_IMAGE}:kronos-gpu"]
}

target "granite-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "granite gpu" }
  tags     = ["${FOMO_IMAGE}:granite-gpu"]
}

target "moirai-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "moirai gpu" }
  tags     = ["${FOMO_IMAGE}:moirai-gpu"]
}

target "tirex-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "tirex gpu" }
  tags     = ["${FOMO_IMAGE}:tirex-gpu"]
}

target "toto-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "toto gpu" }
  tags     = ["${FOMO_IMAGE}:toto-gpu"]
}

target "mantis-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "mantis gpu" }
  tags     = ["${FOMO_IMAGE}:mantis-gpu"]
}

target "full-gpu" {
  inherits = ["_common"]
  args     = { FOMO_EXTRAS = "full gpu" }
  tags     = ["${FOMO_IMAGE}:full-gpu"]
}
