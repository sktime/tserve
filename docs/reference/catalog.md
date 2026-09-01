# Model catalog

Registry ids from [`SKTIME_REGISTRY`][fomo.runtime.registry.sktime_registry.SKTIME_REGISTRY]. These are ids the server *can* load. Nothing here is loaded until `--load-models` / `load_models` selects it. `GET /models` is the loaded list, not this table. See [Loaded vs catalog](../concepts/loaded-vs-catalog.md).

Do not invent ids. If it is not in this table, it is not a registry key. Craft strings stay private to the catalog; [`ModelInfo`][fomo.types.models.ModelInfo] does not expose specs. [`SktimeExecutor.load`][fomo.runtime.executors.sktime.executor.SktimeExecutor.load] calls `sktime.registry.craft(spec)` when `source` is `registry`.

`naive` is `NaiveForecaster()` — no Hub download. The other specs point at Hugging Face (or equivalent) checkpoints; first load pulls weights and needs the `sktime` extra. See [Extras and Hub weights](../how-to/extras.md).

FoMo does not ship a capability matrix. Quantile support is the estimator's (`predict_quantiles`); there is no FoMo flag.

| id | estimator |
| --- | --- |
| `naive` | `NaiveForecaster` |
| `chronos-2` | `Chronos2Forecaster` |
| `chronos-bolt-tiny` | `ChronosForecaster` |
| `kronos` | `KronosForecaster` |
| `moirai-2.0-r-small` | `Moirai2Forecaster` |
| `moirai-1.0-r-small` | `MOIRAIForecaster` |
| `ttm-r2-512-96` | `TinyTimeMixerForecaster` |
| `momentfm` | `MomentFMAnomalyDetector` |
| `timemoe` | `TimeMoEForecaster` |
| `tirex` | `TiRexForecaster` |
| `toto` | `TotoForecaster` |
| `flowstate` | `FlowStateForecaster` |
| `tspulse` | `TSPulseAnomalyDetector` |
| `timesfm-2.5-200m` | `TimesFM2Forecaster` |
| `toto-2.0-22m` | `Toto2Forecaster` |
| `sundial` | `SundialForecaster` |
| `timer` | `TimerForecaster` |
| `patchtsmixer` | `PatchTSMixerForecaster` |
| `falcontst` | `FalconTSTForecaster` |
| `timer-s1` | `TimerS1Forecaster` |
| `windfm` | `WindFMForecaster` |
| `mira` | `MIRAForecaster` |
| `patchtst` | `PatchTSTForecaster` |
| `cisctsm` | `CiscoTSMForecaster` |
| `timesfm` | `TimesFMForecaster` |
| `aurora` | `AuroraForecaster` |
| `lagllama` | `LagLlamaForecaster` |
| `falconx` | `FalconXForecaster` |
