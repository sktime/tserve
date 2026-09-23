### TimesFM 3

<div class="tserve-meta" markdown="span">
<span class="tserve-meta-item">:material-function-variant: [`TimesFM3Forecaster`](https://www.sktime.net/docs/api-reference/sktimeforecastingtimesfm3timesfm3forecaster/)</span>
<span class="tserve-meta-item">:material-package-variant: extra [`timesfm3`](timesfm3.md)</span>
<span class="tserve-meta-item">:material-counter: 1 model</span>
</div>

<div class="tserve-caps" markdown="span">
<span class="tserve-cap tserve-cap--on">:material-check: [multivariate](../client/data.md#targets)</span>
<span class="tserve-cap tserve-cap--on">:material-check: [exogenous](../client/data.md#future-and-static-data)</span>
<span class="tserve-cap tserve-cap--on">:material-check: [quantiles](../client/data.md#quantiles)</span>
</div>

The registry sets `license_accepted=True`. Weights use the [TimesFM non-commercial license](https://huggingface.co/google/timesfm-3.0-pytorch/blob/main/LICENSE). Point forecasts are the median. Native quantile levels are `0.1` through `0.9`.

| model | checkpoint |
| --- | --- |
| `timesfm_3` | [google/timesfm-3.0-pytorch](https://huggingface.co/google/timesfm-3.0-pytorch) |
