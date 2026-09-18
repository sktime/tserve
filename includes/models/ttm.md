### TTM

`TinyTimeMixerForecaster` &middot; extra [`hub`](hub.md) &middot; 70 models
&middot; no [quantiles](../client/data.md#quantiles)

IBM Granite Tiny Time Mixers. Models are `{revision}-{context}-{horizon}`, with
optional `-lite` or `-l1`. The four short models instead take the forecaster
default revision, and `ttm` its default repo too.

#### TTM defaults

| model | repo | revision |
| --- | --- | --- |
| `ttm` | forecaster default (`ibm/TTM`) | forecaster default (`main`) |
| `ttm-r1` | [ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1) | forecaster default (`main`) |
| `ttm-r2` | [ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2) | forecaster default (`main`) |
| `ttm-r3` | [ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | forecaster default (`main`) |

#### TTM r1

[ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1)

| model | context | horizon |
| --- | --- | --- |
| `ttm-r1-512-96` | 512 | 96 |
| `ttm-r1-1024-96` | 1024 | 96 |

#### TTM r2

[ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2)

| model | context | horizon |
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

#### TTM r2.1

Same Hub repo as [r2](#ttm-r2). `-l1` is the L1 checkpoint.

| model | context | horizon | variant |
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

#### TTM r3

[ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3).
Each model has a `-lite` sibling.

| model | lite | context | horizon |
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
