### TTM

<div class="tserve-meta" markdown="span">
<span class="tserve-meta-item">:material-function-variant: [`TinyTimeMixerForecaster`](https://www.sktime.net/docs/api-reference/sktimeforecastingttmtinytimemixerforecaster/)</span>
<span class="tserve-meta-item">:material-package-variant: extra [`hub`](hub.md)</span>
<span class="tserve-meta-item">:material-counter: 70 models</span>
</div>

<div class="tserve-caps" markdown="span">
<span class="tserve-cap tserve-cap--on">:material-check: [multivariate](../client/data.md#targets)</span>
<span class="tserve-cap tserve-cap--on">:material-check: [exogenous](../client/data.md#future-and-static-data)</span>
<span class="tserve-cap tserve-cap--off">:material-minus: [quantiles](../client/data.md#quantiles)</span>
</div>

IBM Granite Tiny Time Mixers. Models are `{revision}-{context}-{horizon}`, with optional `-lite` or `-l1`. The four short models instead take the forecaster default revision, and `ttm` its default repo too.

#### TTM defaults

| model | repo | revision |
| --- | --- | --- |
| `ttm` | forecaster default (`ibm/TTM`) | forecaster default (`main`) |
| `ttm_r1` | [ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1) | forecaster default (`main`) |
| `ttm_r2` | [ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2) | forecaster default (`main`) |
| `ttm_r3` | [ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | forecaster default (`main`) |

#### TTM r1

[ibm-granite/granite-timeseries-ttm-r1](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r1)

| model | context | horizon |
| --- | --- | --- |
| `ttm_r1_512_96` | 512 | 96 |
| `ttm_r1_1024_96` | 1024 | 96 |

#### TTM r2

[ibm-granite/granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2)

| model | context | horizon |
| --- | --- | --- |
| `ttm_r2_512_96` | 512 | 96 |
| `ttm_r2_512_192` | 512 | 192 |
| `ttm_r2_512_336` | 512 | 336 |
| `ttm_r2_512_720` | 512 | 720 |
| `ttm_r2_1024_96` | 1024 | 96 |
| `ttm_r2_1024_192` | 1024 | 192 |
| `ttm_r2_1024_336` | 1024 | 336 |
| `ttm_r2_1024_720` | 1024 | 720 |
| `ttm_r2_1536_96` | 1536 | 96 |
| `ttm_r2_1536_192` | 1536 | 192 |
| `ttm_r2_1536_336` | 1536 | 336 |
| `ttm_r2_1536_720` | 1536 | 720 |

#### TTM r2.1

Same Hub repo as [r2](#ttm-r2). `-l1` is the L1 checkpoint.

| model | context | horizon | variant |
| --- | --- | --- | --- |
| `ttm_r2_1_52_16` | 52 | 16 | |
| `ttm_r2_1_52_16_l1` | 52 | 16 | L1 |
| `ttm_r2_1_90_30` | 90 | 30 | |
| `ttm_r2_1_90_30_l1` | 90 | 30 | L1 |
| `ttm_r2_1_180_60_l1` | 180 | 60 | L1 |
| `ttm_r2_1_360_60_l1` | 360 | 60 | L1 |
| `ttm_r2_1_512_48` | 512 | 48 | |
| `ttm_r2_1_512_48_l1` | 512 | 48 | L1 |
| `ttm_r2_1_512_96` | 512 | 96 | |
| `ttm_r2_1_512_96_l1` | 512 | 96 | L1 |

#### TTM r3

[ibm-granite/granite-timeseries-ttm-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3). Each model has a `-lite` sibling.

| model | lite | context | horizon |
| --- | --- | --- | --- |
| `ttm_r3_52_16` | `ttm_r3_52_16_lite` | 52 | 16 |
| `ttm_r3_90_30` | `ttm_r3_90_30_lite` | 90 | 30 |
| `ttm_r3_156_16` | `ttm_r3_156_16_lite` | 156 | 16 |
| `ttm_r3_180_60` | `ttm_r3_180_60_lite` | 180 | 60 |
| `ttm_r3_360_60` | `ttm_r3_360_60_lite` | 360 | 60 |
| `ttm_r3_512_30` | `ttm_r3_512_30_lite` | 512 | 30 |
| `ttm_r3_512_48` | `ttm_r3_512_48_lite` | 512 | 48 |
| `ttm_r3_512_96` | `ttm_r3_512_96_lite` | 512 | 96 |
| `ttm_r3_512_336` | `ttm_r3_512_336_lite` | 512 | 336 |
| `ttm_r3_768_48` | `ttm_r3_768_48_lite` | 768 | 48 |
| `ttm_r3_1024_48` | `ttm_r3_1024_48_lite` | 1024 | 48 |
| `ttm_r3_1024_96` | `ttm_r3_1024_96_lite` | 1024 | 96 |
| `ttm_r3_1024_720` | `ttm_r3_1024_720_lite` | 1024 | 720 |
| `ttm_r3_1536_96` | `ttm_r3_1536_96_lite` | 1536 | 96 |
| `ttm_r3_1536_720` | `ttm_r3_1536_720_lite` | 1536 | 720 |
| `ttm_r3_2048_96` | `ttm_r3_2048_96_lite` | 2048 | 96 |
| `ttm_r3_2048_720` | `ttm_r3_2048_720_lite` | 2048 | 720 |
| `ttm_r3_2560_96` | `ttm_r3_2560_96_lite` | 2560 | 96 |
| `ttm_r3_2560_720` | `ttm_r3_2560_720_lite` | 2560 | 720 |
| `ttm_r3_3072_96` | `ttm_r3_3072_96_lite` | 3072 | 96 |
| `ttm_r3_3072_720` | `ttm_r3_3072_720_lite` | 3072 | 720 |
