The extra name is the CPU image tag. GPU tags are `{extra}-gpu`. There is no `:base-gpu`.

`kronos` is built on `base`, so it cannot load Chronos Bolt, TTM, or TimesFM. Every extra that pulls `hf` — `hub`, `chronos`, `granite`, `moirai`, `tirex`, `tirex2`, `toto`, `mantis`, `timesfm3`, `t0`, `tafsut`, and `full` — can.

`full` is `chronos`, `kronos`, `granite`, `moirai`, `tirex`, `tirex2`, `toto`, `mantis`, `timesfm3`, `t0`, and `tafsut`. `client`, `http`, `gpu`, `dev`, `docs`, and `all-extras` are not model families. `gpu` selects the torch index for uv on a clone only. Pip ignores `gpu` and installs CUDA torch from PyPI (MPS on macOS). Moirai pins `gluonts`, `lightning`, and `hydra-core` when `python_version < '3.14'`.

**added** counts checkpoints that extra contributes. `full` is the total, including `naive`.

| extra | CPU tag | GPU tag | families | added | example |
| --- | --- | --- | --- | --- | --- |
| `server` | [`:base`](https://hub.docker.com/r/sktime/tserve/tags?name=base) | — | Naive | 1 | `naive` |
| `hub` | [`:hub`](https://hub.docker.com/r/sktime/tserve/tags?name=hub) | [`:hub-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=hub-gpu) | Chronos Bolt, Chronos T5, TTM, TimesFM 2.x | 81 | `chronos_bolt` |
| `chronos` | [`:chronos`](https://hub.docker.com/r/sktime/tserve/tags?name=chronos) | [`:chronos-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=chronos-gpu) | Chronos-2 | 3 | `chronos_2` |
| `kronos` | [`:kronos`](https://hub.docker.com/r/sktime/tserve/tags?name=kronos) | [`:kronos-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=kronos-gpu) | Kronos, WindFM | 5 | `kronos` |
| `granite` | [`:granite`](https://hub.docker.com/r/sktime/tserve/tags?name=granite) | [`:granite-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=granite-gpu) | FlowState | 2 | `flowstate` |
| `moirai` | [`:moirai`](https://hub.docker.com/r/sktime/tserve/tags?name=moirai) | [`:moirai-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=moirai-gpu) | Moirai 2, Moirai 1.x, Lag-Llama | 8 | `moirai_2` |
| `tirex` | [`:tirex`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex) | [`:tirex-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex-gpu) | TiRex | 2 | `tirex` |
| `tirex2` | [`:tirex2`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex2) | [`:tirex2-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=tirex2-gpu) | TiRex-2 | 4 | `tirex_2` |
| `toto` | [`:toto`](https://hub.docker.com/r/sktime/tserve/tags?name=toto) | [`:toto-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=toto-gpu) | Toto-2 | 5 | `toto_2_0_4m` |
| `mantis` | [`:mantis`](https://hub.docker.com/r/sktime/tserve/tags?name=mantis) | [`:mantis-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=mantis-gpu) | Mantis | 3 | `mantis_8m` |
| `timesfm3` | [`:timesfm3`](https://hub.docker.com/r/sktime/tserve/tags?name=timesfm3) | [`:timesfm3-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=timesfm3-gpu) | TimesFM 3 | 1 | `timesfm_3` |
| `t0` | [`:t0`](https://hub.docker.com/r/sktime/tserve/tags?name=t0) | [`:t0-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=t0-gpu) | T0 | 1 | `t0` |
| `tafsut` | [`:tafsut`](https://hub.docker.com/r/sktime/tserve/tags?name=tafsut) | [`:tafsut-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=tafsut-gpu) | Tafsut | 1 | `tafsut` |
| `full` | [`:full`](https://hub.docker.com/r/sktime/tserve/tags?name=full) | [`:full-gpu`](https://hub.docker.com/r/sktime/tserve/tags?name=full-gpu) | all of the above | 117 | `chronos_2` |
