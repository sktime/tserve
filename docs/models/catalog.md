# Catalog

Ids the server can load. Nothing here is loaded until `--load-models` / `load_models` selects it — see [Load models](index.md). TTM ids are `{revision}-{context}-{horizon}`, with optional `-lite` / `-l1`.

## Baseline

| id | estimator |
| --- | --- |
| `naive` | `NaiveForecaster` |

## Chronos

| id | estimator |
| --- | --- |
| `chronos-2`, `chronos-2-small`, `chronos-2-synth` | `Chronos2Forecaster` |
| `chronos-bolt-tiny`, `chronos-bolt-mini`, `chronos-bolt-small`, `chronos-bolt-base` | `ChronosForecaster` |
| `chronos-t5-tiny`, `chronos-t5-mini`, `chronos-t5-small`, `chronos-t5-base`, `chronos-t5-large` | `ChronosForecaster` |

## Kronos / WindFM

| id | estimator |
| --- | --- |
| `kronos`, `kronos-mini`, `kronos-base` | `KronosForecaster` |
| `windfm`, `windfm-robust` | `WindFMForecaster` |

## Moirai

| id | estimator |
| --- | --- |
| `moirai-2` | `Moirai2Forecaster` |
| `moirai-1.0-r-small`, `moirai-1.0-r-base`, `moirai-1.0-r-large` | `MOIRAIForecaster` |
| `moirai-1.1-r-small`, `moirai-1.1-r-base`, `moirai-1.1-r-large` | `MOIRAIForecaster` |

## TimesFM / Toto / FlowState / TiRex

| id | estimator |
| --- | --- |
| `timesfm-2.5`, `timesfm-2` | `TimesFM2Forecaster` |
| `toto-2.0-4m`, `toto-2.0-22m`, `toto-2.0-313m`, `toto-2.0-1b`, `toto-2.0-2.5b` | `Toto2Forecaster` |
| `flowstate`, `flowstate-granite` | `FlowStateForecaster` |
| `tirex`, `tirex-1.1-gifteval` | `TiRexForecaster` |

## TTM

`TinyTimeMixerForecaster`. r1:

| id | context | horizon |
| --- | --- | --- |
| `ttm-r1-512-96` | 512 | 96 |
| `ttm-r1-1024-96` | 1024 | 96 |

r2:

| id | context | horizon |
| --- | --- | --- |
| `ttm-r2-512-96` | 512 | 96 |
| `ttm-r2-512-192` | 512 | 192 |
| `ttm-r2-512-336` | 512 | 336 |
| `ttm-r2-512-720` | 512 | 720 |
| `ttm-r2-1024-96` | 1024 | 96 |
| `ttm-r2-1024-192` | 1024 | 192 |
| `ttm-r2-1024-336` | 1024 | 336 |
| `ttm-r2-1024-720` | 1024 | 720 |
| `ttm-r2-1536-96` | 1536 | 96 |
| `ttm-r2-1536-192` | 1536 | 192 |
| `ttm-r2-1536-336` | 1536 | 336 |
| `ttm-r2-1536-720` | 1536 | 720 |

r2.1 (`-l1` is the L1 checkpoint):

| id | context | horizon | variant |
| --- | --- | --- | --- |
| `ttm-r2.1-52-16` | 52 | 16 | |
| `ttm-r2.1-52-16-l1` | 52 | 16 | L1 |
| `ttm-r2.1-90-30` | 90 | 30 | |
| `ttm-r2.1-90-30-l1` | 90 | 30 | L1 |
| `ttm-r2.1-180-60-l1` | 180 | 60 | L1 |
| `ttm-r2.1-360-60-l1` | 360 | 60 | L1 |
| `ttm-r2.1-512-48` | 512 | 48 | |
| `ttm-r2.1-512-48-l1` | 512 | 48 | L1 |
| `ttm-r2.1-512-96` | 512 | 96 | |
| `ttm-r2.1-512-96-l1` | 512 | 96 | L1 |

r3 (each id has a `-lite` sibling):

| id | lite | context | horizon |
| --- | --- | --- | --- |
| `ttm-r3-52-16` | `ttm-r3-52-16-lite` | 52 | 16 |
| `ttm-r3-90-30` | `ttm-r3-90-30-lite` | 90 | 30 |
| `ttm-r3-156-16` | `ttm-r3-156-16-lite` | 156 | 16 |
| `ttm-r3-180-60` | `ttm-r3-180-60-lite` | 180 | 60 |
| `ttm-r3-360-60` | `ttm-r3-360-60-lite` | 360 | 60 |
| `ttm-r3-512-30` | `ttm-r3-512-30-lite` | 512 | 30 |
| `ttm-r3-512-48` | `ttm-r3-512-48-lite` | 512 | 48 |
| `ttm-r3-512-96` | `ttm-r3-512-96-lite` | 512 | 96 |
| `ttm-r3-512-336` | `ttm-r3-512-336-lite` | 512 | 336 |
| `ttm-r3-768-48` | `ttm-r3-768-48-lite` | 768 | 48 |
| `ttm-r3-1024-48` | `ttm-r3-1024-48-lite` | 1024 | 48 |
| `ttm-r3-1024-96` | `ttm-r3-1024-96-lite` | 1024 | 96 |
| `ttm-r3-1024-720` | `ttm-r3-1024-720-lite` | 1024 | 720 |
| `ttm-r3-1536-96` | `ttm-r3-1536-96-lite` | 1536 | 96 |
| `ttm-r3-1536-720` | `ttm-r3-1536-720-lite` | 1536 | 720 |
| `ttm-r3-2048-96` | `ttm-r3-2048-96-lite` | 2048 | 96 |
| `ttm-r3-2048-720` | `ttm-r3-2048-720-lite` | 2048 | 720 |
| `ttm-r3-2560-96` | `ttm-r3-2560-96-lite` | 2560 | 96 |
| `ttm-r3-2560-720` | `ttm-r3-2560-720-lite` | 2560 | 720 |
| `ttm-r3-3072-96` | `ttm-r3-3072-96-lite` | 3072 | 96 |
| `ttm-r3-3072-720` | `ttm-r3-3072-720-lite` | 3072 | 720 |

## Other

| id | estimator |
| --- | --- |
| `lagllama` | `LagLlamaForecaster` |
| `mantis`, `mantis-8m`, `mantis-plus` | `MantisForecaster` |

FoMo does not ship a capability matrix. Quantile support is the estimator's `predict_quantiles`; there is no FoMo flag. Asking an id that cannot return quantiles fails the request (`ChronosForecaster` / Chronos Bolt does not). `naive` does.
