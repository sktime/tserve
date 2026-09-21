### Mantis

<div class="tserve-meta" markdown="span">
<span class="tserve-meta-item">:material-function-variant: [`MantisForecaster`](https://www.sktime.net/docs/api-reference/sktimeforecastingmantismantisforecaster/)</span>
<span class="tserve-meta-item">:material-package-variant: extra [`mantis`](mantis.md)</span>
<span class="tserve-meta-item">:material-counter: 3 models</span>
</div>

<div class="tserve-caps" markdown="span">
<span class="tserve-cap tserve-cap--on">:material-check: [multivariate](../client/data.md#targets)</span>
<span class="tserve-cap tserve-cap--off">:material-minus: [exogenous](../client/data.md#future-and-static-data)</span>
<span class="tserve-cap tserve-cap--off">:material-minus: [quantiles](../client/data.md#quantiles)</span>
</div>

Embeddings plus an sklearn head. `context_length` is 127, so `past` must be longer than that.

| model | checkpoint |
| --- | --- |
| `mantis` | [paris-noah/MantisV2](https://huggingface.co/paris-noah/MantisV2) |
| `mantis_8m` | [paris-noah/Mantis-8M](https://huggingface.co/paris-noah/Mantis-8M) |
| `mantis_plus` | [paris-noah/MantisPlus](https://huggingface.co/paris-noah/MantisPlus) |
