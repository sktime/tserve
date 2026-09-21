### Naive

<div class="tserve-meta" markdown="span">
<span class="tserve-meta-item">:material-function-variant: `NaiveForecaster`</span>
<span class="tserve-meta-item">:material-package-variant: extra [`server`](base.md)</span>
<span class="tserve-meta-item">:material-counter: 1 model</span>
</div>

<div class="tserve-caps" markdown="span">
<span class="tserve-cap tserve-cap--off">:material-minus: [multivariate](../client/data.md#targets)</span>
<span class="tserve-cap tserve-cap--off">:material-minus: [exogenous](../client/data.md#future-and-static-data)</span>
<span class="tserve-cap tserve-cap--on">:material-check: [quantiles](../client/data.md#quantiles)</span>
</div>

Drift strategy. No weights, no Hugging Face download. Always loaded so you can test the server; name another catalog model for a real forecast.

| model | checkpoint |
| --- | --- |
| `naive` | none |
