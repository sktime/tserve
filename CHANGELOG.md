# Changelog

All notable changes to TServe are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Until 1.0, a minor release may change the HTTP API, the Python client, or the CLI.

## [Unreleased]

### Added

- Docker images have a `HEALTHCHECK` on `GET /health`, so `docker ps` and Compose `service_healthy` report when every model is loaded. ([#150](https://github.com/sktime/tserve/issues/150))

## [0.1.0] - 2026-09-24

First release on PyPI and Docker Hub.
