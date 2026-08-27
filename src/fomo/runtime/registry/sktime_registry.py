"""Catalog of sktime craft specs keyed by registry id.

``SKTIME_REGISTRY`` lists ids the server *can* load (``naive``,
``chronos-2``, …). It is not the loaded-model list: ``GET /models``
returns only models ``bootstrap(load_models)`` / ``--load-models``
actually instantiated. Registry ids are not executor names (``sktime``,
``pytorch-forecasting``, ``custom``).

Craft strings stay private to this catalog. ``ModelInfo`` is
listing-only (``id``, ``executor``, ``source``) and does not expose
specs. ``SktimeExecutor.load`` calls
``sktime.registry.craft(SKTIME_REGISTRY[model]["spec"])`` when
``source`` is ``registry``.

See Also
--------
fomo.runtime.registry.resolver.resolve_model
    String ids in this catalog become ``source="registry"``.
fomo.runtime.bootstrap.bootstrap
    Selects which catalog ids (if any) to load.
"""

from fomo.runtime.registry import BASE_REGISTRY_TYPE

# Catalog of ids the server can load. Nothing here is loaded until
# --load-models / load_models selects it.
# Checkout https://github.com/sktime/fomo/issues/1
# Craft strings stay private to the registry; ModelInfo is listing-only.
SKTIME_REGISTRY: BASE_REGISTRY_TYPE = {
    "naive": {
        "spec": "NaiveForecaster()",
    },
    "chronos-2": {
        "spec": 'Chronos2Forecaster(model_path="amazon/chronos-2", config={"device_map": "auto"})',
    },
    "chronos": {
        "spec": 'ChronosForecaster(model_path="amazon/chronos-bolt-tiny", config={"device_map": "auto"})',
    },
    "kronos": {
        "spec": 'KronosForecaster(model_path="NeoQuasar/Kronos-small")',
    },
    "moirai-2": {
        "spec": 'Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")',
    },
    "ttm": {
        "spec": 'TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r2")',
    },
    "momentfm": {
        "spec": 'MomentFMAnomalyDetector(pretrained_model_name_or_path="AutonLab/MOMENT-1-small", device="auto")',
    },
    "timemoe": {
        "spec": 'TimeMoEForecaster(model_path="Maple728/TimeMoE-50M", config={"device_map": "auto"})',
    },
    "tirex": {
        "spec": 'TiRexForecaster(model="NX-AI/TiRex")',
    },
    "moirai": {
        "spec": 'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-small", map_location="auto")',
    },
    "toto": {
        "spec": 'TotoForecaster(model_path="Datadog/Toto-Open-Base-1.0")',
    },
    "flowstate": {
        "spec": 'FlowStateForecaster(model_path="ibm-research/flowstate")',
    },
    "tspulse": {
        "spec": 'TSPulseAnomalyDetector(model_path="ibm-granite/granite-timeseries-tspulse-r1")',
    },
    "timesfm-2.5": {
        "spec": 'TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers", device_map="auto")',
    },
    "toto-2": {
        "spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-22m")',
    },
    "sundial": {
        "spec": 'SundialForecaster(model_path="thuml/sundial-base-128m")',
    },
    "timer": {
        "spec": 'TimerForecaster(model_name="thuml/timer-base-84m")',
    },
    "patchtsmixer": {
        "spec": 'PatchTSMixerForecaster(model_path="ibm-granite/granite-timeseries-patchtsmixer")',
    },
    "falcontst": {
        "spec": 'FalconTSTForecaster(model_path="ant-intl/Falcon-TST_Large", device_map="auto")',
    },
    "timer-s1": {
        "spec": 'TimerS1Forecaster(model_path="bytedance-research/Timer-S1", device_map="auto")',
    },
    "windfm": {
        "spec": 'WindFMForecaster(model_path="NeoQuasar/WindFM")',
    },
    "mira": {
        "spec": 'MIRAForecaster(model_path="MIRA-Mode/MIRA")',
    },
    "patchtst": {
        "spec": 'PatchTSTForecaster(model_path="namctin/patchtst_etth1_forecast")',
    },
    "cisctsm": {
        "spec": 'CiscoTSMForecaster(model_path="cisco-ai/cisco-time-series-model-1.0-preview", backend="gpu")',
    },
    "timesfm": {
        "spec": 'TimesFMForecaster(repo_id="google/timesfm-1.0-200m")',
    },
    "aurora": {
        "spec": 'AuroraForecaster(repo_id="DecisionIntelligence/Aurora")',
    },
    "lagllama": {
        "spec": 'LagLlamaForecaster(ckpt_path="time-series-foundation-models/Lag-Llama")',
    },
    "falconx": {
        "spec": "FalconXForecaster()",
    },
}
"""Catalog of loadable sktime model ids; see the module docstring."""
