from fomo.types import ModelInfo, ModelsResult
from typing import Any

# Catalog of aliases the server can load. Nothing here is loaded until
# --load-models / load_models selects it.
# Checkout https://github.com/sktime/fomo/issues/1
# Craft strings stay private to the registry; ModelInfo is listing-only.
_REGISTRY: list[tuple[str, str]] = [
    ("dummy", "NaiveForecaster()"),
    ("chronos2", 'Chronos2Forecaster(model_path="amazon/chronos-2")'),
    ("chronos", 'ChronosForecaster(model_path="amazon/chronos-bolt-tiny")'),
    ("kronos", 'KronosForecaster(model_path="NeoQuasar/Kronos-small")'),
    ("moirai2", 'Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")'),
    ("ttm", 'TinyTimeMixerForecaster(model_path="ibm-granite/granite-timeseries-ttm-r2")'),
    (
        "momentfm",
        'MomentFMAnomalyDetector(pretrained_model_name_or_path="AutonLab/MOMENT-1-small")',
    ),
    ("timemoe", 'TimeMoEForecaster(model_path="Maple728/TimeMoE-50M")'),
    ("tirex", 'TiRexForecaster(model="NX-AI/TiRex")'),
    ("moirai", 'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-small")'),
    ("toto", 'TotoForecaster(model_path="Datadog/Toto-Open-Base-1.0")'),
    ("flowstate", 'FlowStateForecaster(model_path="ibm-research/flowstate")'),
    (
        "tspulse",
        'TSPulseAnomalyDetector(model_path="ibm-granite/granite-timeseries-tspulse-r1")',
    ),
    (
        "timesfm2.5",
        'TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers")',
    ),
    ("toto2", 'Toto2Forecaster(model_path="Datadog/Toto-2.0-22m")'),
    ("sundial", 'SundialForecaster(model_path="thuml/sundial-base-128m")'),
    ("timer", 'TimerForecaster(model_name="thuml/timer-base-84m")'),
    (
        "patchtsmixer",
        'PatchTSMixerForecaster(model_path="ibm-granite/granite-timeseries-patchtsmixer")',
    ),
    ("falcontst", 'FalconTSTForecaster(model_path="ant-intl/Falcon-TST_Large")'),
    ("timers1", 'TimerS1Forecaster(model_path="bytedance-research/Timer-S1")'),
    ("windfm", 'WindFMForecaster(model_path="NeoQuasar/WindFM")'),
    ("mira", 'MIRAForecaster(model_path="MIRA-Mode/MIRA")'),
    ("patchtst", 'PatchTSTForecaster(model_path="namctin/patchtst_etth1_forecast")'),
    (
        "cisctsm",
        'CiscoTSMForecaster(model_path="cisco-ai/cisco-time-series-model-1.0-preview")',
    ),
    ("timesfm", 'TimesFMForecaster(repo_id="google/timesfm-1.0-200m")'),
    ("aurora", 'AuroraForecaster(repo_id="DecisionIntelligence/Aurora")'),
    (
        "lagllama",
        'LagLlamaForecaster(ckpt_path="time-series-foundation-models/Lag-Llama")',
    ),
    ("falconx", "FalconXForecaster()"),
]

_PRE_REGISTERED = [
    ModelInfo(alias=alias, executor="sktime", source="registry") for alias, _ in _REGISTRY
]
_CRAFT = dict(_REGISTRY)
_PRE_REGISTERED_BY_ALIAS = {model.alias: model for model in _PRE_REGISTERED}

PRE_REGISTERED_MODELS = ModelsResult(models=_PRE_REGISTERED)


def get_pre_registered(alias: str) -> ModelInfo:
    model = _PRE_REGISTERED_BY_ALIAS.get(alias)
    if model is None:
        known = ", ".join(_PRE_REGISTERED_BY_ALIAS)
        raise ValueError(f"unknown pre-registered model {alias!r}, choose one of: {known}")
    return model


def get_registry_craft(alias: str) -> str:
    get_pre_registered(alias)
    return _CRAFT[alias]


def resolve_model(item: Any) -> ModelInfo:
    if isinstance(item, ModelInfo):
        return item

    if isinstance(item, str) and item in _CRAFT:
        return ModelInfo(alias=item, executor="sktime", source="registry")

    raise TypeError(
        f"expected alias str, got {type(item).__name__}; "
        f"choose one of: {', '.join(_CRAFT.keys())}"
    )
