"""Catalog of sktime craft specs keyed by registry id.

``SKTIME_REGISTRY`` lists ids the server *can* load (``naive``,
``chronos_2``, ``chronos_bolt_small``, …). It is not the loaded-model
list: ``GET /models`` returns only models ``bootstrap(model)`` /
leftover CLI positionals actually instantiated. Registry ids are not executor
names (``sktime``, ``pytorch-forecasting``, ``custom``).

Ids are valid Python identifiers (PEP 440-style: ``-`` and ``.`` become
``_``) and name the checkpoint (family, version, size or revision).

Craft strings stay private to this catalog. ``ModelInfo`` is
listing-only (``id``, ``executor``, ``source``) and does not expose
specs. Each entry also carries ``group``: the family extra and
``full``, smallest first (e.g. ``moirai`` → ``("moirai", "full")``).
The extra name is the CPU Docker tag except ``server`` → ``base``.
``SktimeExecutor.load`` calls
``sktime.registry.craft(SKTIME_REGISTRY[model]["spec"])`` when
``source`` is ``registry``.

See Also
--------
tserve.runtime.registry.resolver.resolve_model
    String ids in this catalog become ``source="registry"``.
tserve.runtime.bootstrap.bootstrap
    Selects which catalog ids (if any) to load.
"""

from tserve.runtime.registry import BASE_REGISTRY_TYPE

# Catalog of ids the server can load. Nothing here is loaded until
# leftover CLI positionals / model selects it.
# Checkout https://github.com/sktime/tserve/issues/1
# Craft strings stay private to the registry; ModelInfo is listing-only.


SKTIME_REGISTRY: BASE_REGISTRY_TYPE = {
    # Statistical baselines. ``naive`` uses drift so trending series are
    # not stuck on a flat last-value forecast.
    "naive": {"spec": 'NaiveForecaster(strategy="drift")'},
    # Chronos-2 (amazon/autogluon). Multivariate + covariates.
    "chronos_2": {
        "spec": (
            'Chronos2Forecaster(model_path="amazon/chronos-2", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_2_small": {
        "spec": (
            'Chronos2Forecaster(model_path="autogluon/chronos-2-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_2_synth": {
        "spec": (
            'Chronos2Forecaster(model_path="autogluon/chronos-2-synth", '
            'config={"device_map": "auto"})'
        )
    },
    # Chronos-Bolt.
    "chronos_bolt": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-tiny", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_bolt_mini": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-mini", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_bolt_small": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_bolt_base": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-base", '
            'config={"device_map": "auto"})'
        )
    },
    # Original Chronos (T5).
    "chronos_t5": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-tiny", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_t5_mini": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-mini", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_t5_small": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_t5_base": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-base", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos_t5_large": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-large", '
            'config={"device_map": "auto"})'
        )
    },
    # Kronos. Pair each model with the tokenizer from the Hub cards.
    "kronos": {
        "spec": (
            'KronosForecaster(model_path="NeoQuasar/Kronos-small", '
            'tokenizer_path="NeoQuasar/Kronos-Tokenizer-base", deterministic=True)'
        )
    },
    "kronos_mini": {
        "spec": (
            'KronosForecaster(model_path="NeoQuasar/Kronos-mini", '
            'tokenizer_path="NeoQuasar/Kronos-Tokenizer-2k", deterministic=True)'
        )
    },
    "kronos_base": {
        "spec": (
            'KronosForecaster(model_path="NeoQuasar/Kronos-base", '
            'tokenizer_path="NeoQuasar/Kronos-Tokenizer-base", deterministic=True)'
        )
    },
    # Moirai 2.0 (small is the only published 2.0 size).
    "moirai_2": {
        "spec": 'Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")'
    },
    # TTM.
    "ttm": {"spec": 'TinyTimeMixerForecaster(fit_strategy="zero-shot")'},
    # TTM r1.
    "ttm_r1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm_r1_512_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'revision="main", fit_strategy="zero-shot")'
        )
    },
    "ttm_r1_1024_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'revision="1024_96_v1", fit_strategy="zero-shot")'
        )
    },
    # TTM r2.
    "ttm_r2": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_512_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="main", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_512_192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_512_336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_512_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-720-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1024_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-96-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1024_192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1024_336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1024_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-720-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1536_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-96-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1536_192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1536_336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1536_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-720-r2", fit_strategy="zero-shot")'
        )
    },
    # TTM r2.1. Same Hub repo as r2, selected by revision.
    "ttm_r2_1_52_16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="52-16-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_52_16_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="52-16-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_90_30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="90-30-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_90_30_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="90-30-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_512_48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-48-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_512_48_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-48-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_512_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-96-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_512_96_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-96-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_180_60_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="180-60-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm_r2_1_360_60_l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="360-60-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    # TTM r3.
    "ttm_r3": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_52_16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_52_16_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="52-16-dec-52-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_90_30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="90-30-dec-90-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_90_30_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="90-30-dec-90-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_156_16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="156-16-dec-52-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_156_16_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="156-16-dec-52-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_180_60": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="180-60-dec-180-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_180_60_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="180-60-dec-180-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_360_60": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="360-60-dec-360-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_360_60_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="360-60-dec-360-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-30-dec-90-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_30_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-30-dec-90-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_48_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-96-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-96-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-336-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_512_336_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-336-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_768_48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="768-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_768_48_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="768-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_48_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1024_720_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1536_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1536_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1536_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_1536_720_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2048_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2048_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2048_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2048_720_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2560_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2560_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2560_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_2560_720_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_3072_96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_3072_96_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_3072_720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm_r3_3072_720_lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    # TTM research r2. Ignored: runtime error (`index out of range in self`).
    # "ttm_research_r2_512_96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="main", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_512_192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_512_336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_512_720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1024_96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-96-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1024_192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1024_336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1024_720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1536_96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-96-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1536_192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1536_336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm_research_r2_1536_720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # Time-MoE. Ignored: incompatible dependency pin (`transformers<=4.40.1`).
    # "timemoe_50m": {
    #     "spec": (
    #         'TimeMoEForecaster(model_path="Maple728/TimeMoE-50M", '
    #         'config={"device_map": "auto"})'
    #     )
    # },
    # "timemoe_200m": {
    #     "spec": (
    #         'TimeMoEForecaster(model_path="Maple728/TimeMoE-200M", '
    #         'config={"device_map": "auto"})'
    #     )
    # },
    # TiRex v1 requires an explicit license acceptance.
    "tirex": {"spec": 'TiRexForecaster(model="NX-AI/TiRex", license_accepted=True)'},
    "tirex_1_1_gifteval": {
        "spec": (
            'TiRexForecaster(model="NX-AI/TiRex-1.1-gifteval", license_accepted=True)'
        )
    },
    # TiRex-2. The three decontaminated checkpoints are gated on Hugging Face.
    "tirex_2": {
        "spec": 'TiRex2Forecaster(model_path="NX-AI/TiRex-2", device="auto")'
    },
    "tirex_2_gifteval_zs": {
        "spec": (
            'TiRex2Forecaster(model_path="NX-AI/TiRex-2-gifteval-zs", device="auto")'
        )
    },
    "tirex_2_gifteval_pretrain": {
        "spec": (
            'TiRex2Forecaster(model_path="NX-AI/TiRex-2-gifteval-pretrain", '
            'device="auto")'
        )
    },
    "tirex_2_fevbench": {
        "spec": 'TiRex2Forecaster(model_path="NX-AI/TiRex-2-fevbench", device="auto")'
    },
    # T0. Gated checkpoint; license_accepted is required.
    "t0": {
        "spec": (
            'T0Forecaster(model_path="theforecastingcompany/t0-alpha", '
            'license_accepted=True)'
        )
    },
    # Tafsut.
    "tafsut": {
        "spec": 'TafsutForecaster(model_path="Tafsut-FM/tafsut-univariate-base")'
    },
    # MOIRAI 1.0 / 1.1. Salesforce safetensors path; map_location auto-picks device.
    "moirai_1_0_r_small": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-small", '
            'map_location="cpu")'
        )
    },
    "moirai_1_0_r_base": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-base", '
            'map_location="cpu")'
        )
    },
    "moirai_1_0_r_large": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-large", '
            'map_location="cpu")'
        )
    },
    "moirai_1_1_r_small": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.1-R-small", '
            'map_location="cpu")'
        )
    },
    "moirai_1_1_r_base": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.1-R-base", '
            'map_location="cpu")'
        )
    },
    "moirai_1_1_r_large": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.1-R-large", '
            'map_location="cpu")'
        )
    },
    # Toto 1.0. Ignored: incompatible dependency pin
    # (`toto-ts>=0.1.3` pins transformers).
    # "toto": {"spec": 'TotoForecaster(model_path="Datadog/Toto-Open-Base-1.0")'},
    # FlowState. Pin r1.1; Hub ``main`` is still v1.0.
    "flowstate": {
        "spec": (
            'FlowStateForecaster(model_path="ibm-research/flowstate", revision="r1.1")'
        )
    },
    "flowstate_granite": {
        "spec": (
            "FlowStateForecaster("
            'model_path="ibm-granite/granite-timeseries-flowstate-r1", '
            'revision="r1.1")'
        )
    },
    # TimesFM 3. Non-commercial weights; license_accepted is required.
    "timesfm_3": {
        "spec": (
            'TimesFM3Forecaster(model_path="google/timesfm-3.0-pytorch", '
            'license_accepted=True)'
        )
    },
    # TimesFM 2.x (transformers).
    "timesfm_2_5": {
        "spec": (
            'TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers", '
            'device_map="auto")'
        )
    },
    "timesfm_2": {
        "spec": (
            'TimesFM2Forecaster(model_path="google/timesfm-2.0-500m-pytorch", '
            'device_map="auto", forward_kwargs={"forecast_context_len": 1024})'
        )
    },
    # Toto 2.0 size grid.
    "toto_2_0_4m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-4m")'},
    "toto_2_0_22m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-22m")'},
    "toto_2_0_313m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-313m")'},
    "toto_2_0_1b": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-1B")'},
    "toto_2_0_2_5b": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-2.5B")'},
    # Sundial. Ignored: incompatible dependency pin (`transformers[torch]~=4.40.0`).
    # "sundial": {"spec": 'SundialForecaster(model_path="thuml/sundial-base-128m")'},
    # Timer. Ignored: incompatible dependency pin (`python<3.13`).
    # "timer": {"spec": 'TimerForecaster(model_name="thuml/timer-base-84m")'},
    # Timer-S1. Ignored: incompatible dependency pin
    # (`transformers[torch]>4.57.0,<5.0.0`).
    # "timer_s1": {
    #     "spec": (
    #         'TimerS1Forecaster(model_path="bytedance-research/Timer-S1", '
    #         'device_map="auto", deterministic=True)'
    #     )
    # },
    # "timer_s1_4bit": {
    #     "spec": (
    #         'TimerS1Forecaster(model_path="sktime/Timer-S1-quantized-4bit", '
    #         'device_map="auto", deterministic=True)'
    #     )
    # },
    # PatchTSMixer. Ignored: runtime error
    # (`mat1 and mat2 shapes cannot be multiplied`).
    # "patchtsmixer": {
    #     "spec": (
    #         "PatchTSMixerForecaster("
    #         'model_path="ibm-granite/granite-timeseries-patchtsmixer", '
    #         'revision="main", train_model=False)'
    #     )
    # },
    # Falcon-TST. Ignored: incompatible dependency pin (`transformers[torch]<5.0.0`).
    # "falcontst": {
    #     "spec": (
    #         'FalconTSTForecaster(model_path="ant-intl/Falcon-TST_Large", '
    #         'device_map="auto")'
    #     )
    # },
    # WindFM. Pair each model with its matching tokenizer.
    "windfm": {
        "spec": (
            'WindFMForecaster(model_path="NeoQuasar/WindFM", '
            'tokenizer_path="NeoQuasar/WindFM-Tokenizer", deterministic=True)'
        )
    },
    "windfm_robust": {
        "spec": (
            'WindFMForecaster(model_path="NeoQuasar/WindFM-robust", '
            'tokenizer_path="NeoQuasar/WindFM-Tokenizer-robust", deterministic=True)'
        )
    },
    # MIRA. Ignored: incompatible dependency pin (`transformers==4.40.1`).
    # "mira": {"spec": 'MIRAForecaster(model_path="MIRA-Mode/MIRA")'},
    # PatchTST. Ignored: runtime error
    # (`input sequence length does not match model configuration`).
    # "patchtst": {
    #     "spec": (
    #         "PatchTSTForecaster("
    #         'model_path="ibm-granite/granite-timeseries-patchtst", '
    #         'fit_strategy="zero-shot")'
    #     )
    # },
    # "patchtst_etth1": {
    #     "spec": (
    #         "PatchTSTForecaster("
    #         'model_path="ibm-research/testing-patchtst_etth1_forecast", '
    #         'fit_strategy="zero-shot")'
    #     )
    # },
    # Cisco TSM. Ignored: incompatible dependency pin
    # (`cisco-tsm` clashes with `granite-tsfm`).
    # "cisctsm": {
    #     "spec": (
    #         'CiscoTSMForecaster(model_path="cisco-ai/cisco-time-series-model-1.0", '
    #         'num_layers=25, backend="gpu")'
    #     )
    # },
    # "cisctsm_preview": {
    #     "spec": (
    #         "CiscoTSMForecaster("
    #         'model_path="cisco-ai/cisco-time-series-model-1.0-preview", '
    #         'num_layers=50, backend="gpu")'
    #     )
    # },
    # TimesFM 1.0. Ignored: incompatible dependency pin (`python>=3.10,<3.11`).
    # "timesfm": {"spec": 'TimesFMForecaster(repo_id="google/timesfm-1.0-200m")'},
    # Aurora Ignored: needed torchvision which is removed in dependency group refactor
    # "aurora": {"spec": 'AuroraForecaster(repo_id="DecisionIntelligence/Aurora")'},
    "lagllama": {
        "spec": (
            'LagLlamaForecaster(ckpt_path="time-series-foundation-models/Lag-Llama")'
        )
    },
    # FalconX Ignored: not an open-source model rather sends API requests
    # "falconx": {"spec": "FalconXForecaster(license_accepted=True)"},
    # Mantis embeddings + sklearn head. Not ignored but see `context_length`.
    "mantis": {
        "spec": (
            'MantisForecaster(checkpoint="paris-noah/MantisV2", model_version="v2", '
            'device="auto", context_length=127)'
        )
    },
    "mantis_8m": {
        "spec": (
            'MantisForecaster(checkpoint="paris-noah/Mantis-8M", model_version="v1", '
            'device="auto", context_length=127)'
        )
    },
    "mantis_plus": {
        "spec": (
            'MantisForecaster(checkpoint="paris-noah/MantisPlus", model_version="v1", '
            'device="auto", context_length=127)'
        )
    },
    # Time-LLM. Ignored: runtime error (`selected index k out of range`).
    # "time_llm": {"spec": 'TimeLLMForecaster(llm_model="GPT2")'},
    # "time_llm_bert": {"spec": 'TimeLLMForecaster(llm_model="BERT")'},
    # "time_llm_llama": {"spec": 'TimeLLMForecaster(llm_model="LLAMA")'},
    # Hugging Face transformers tourism-monthly. Ignored: runtime error
    # (`'NoneType' object does not support item assignment`).
    # "autoformer": {
    #     "spec": (
    #         "HFTransformersForecaster("
    #         'model_path="huggingface/autoformer-tourism-monthly", '
    #         'fit_strategy="minimal", deterministic=True)'
    #     )
    # },
    # "informer": {
    #     "spec": (
    #         "HFTransformersForecaster("
    #         'model_path="huggingface/informer-tourism-monthly", '
    #         'fit_strategy="minimal", deterministic=True)'
    #     )
    # },
    # "tstransformer": {
    #     "spec": (
    #         "HFTransformersForecaster("
    #         'model_path="huggingface/time-series-transformer-tourism-monthly", '
    #         'fit_strategy="minimal", deterministic=True)'
    #     )
    # },
}
"""Catalog of loadable sktime model ids; see the module docstring."""


def _group_for(model_id: str) -> tuple[str, ...]:
    if model_id == "naive":
        family = "server"
    elif model_id.startswith("chronos_2"):
        family = "chronos"
    elif model_id.startswith("timesfm_3"):
        family = "timesfm3"
    elif model_id.startswith(("chronos_", "ttm", "timesfm")):
        family = "hub"
    elif model_id.startswith(("kronos", "windfm")):
        family = "kronos"
    elif model_id.startswith("flowstate"):
        family = "granite"
    elif model_id.startswith(("moirai_", "lagllama")):
        family = "moirai"
    elif model_id.startswith("tirex_2"):
        family = "tirex2"
    elif model_id.startswith("tirex"):
        family = "tirex"
    elif model_id.startswith("t0"):
        family = "t0"
    elif model_id.startswith("tafsut"):
        family = "tafsut"
    elif model_id.startswith("toto_"):
        family = "toto"
    elif model_id.startswith("mantis"):
        family = "mantis"
    else:
        raise KeyError(f"no group mapping for registry id {model_id!r}")
    return (family, "full")


for _id, _meta in SKTIME_REGISTRY.items():
    _meta["group"] = _group_for(_id)
