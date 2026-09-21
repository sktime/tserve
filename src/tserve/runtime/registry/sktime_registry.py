"""Catalog of sktime craft specs keyed by registry id.

``SKTIME_REGISTRY`` lists ids the server *can* load (``naive``,
``chronos-2``, ``chronos-bolt-small``, …). It is not the loaded-model
list: ``GET /models`` returns only models ``bootstrap(model)`` /
``--model`` actually instantiated. Registry ids are not executor
names (``sktime``, ``pytorch-forecasting``, ``custom``).

Ids are kebab-case and name the checkpoint (family, version, size or
revision).

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
# --model / model selects it.
# Checkout https://github.com/sktime/tserve/issues/1
# Craft strings stay private to the registry; ModelInfo is listing-only.


SKTIME_REGISTRY: BASE_REGISTRY_TYPE = {
    # Statistical baselines. ``naive`` uses drift so trending series are
    # not stuck on a flat last-value forecast.
    "naive": {"spec": 'NaiveForecaster(strategy="drift")'},
    # Chronos-2 (amazon/autogluon). Multivariate + covariates.
    "chronos-2": {
        "spec": (
            'Chronos2Forecaster(model_path="amazon/chronos-2", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-2-small": {
        "spec": (
            'Chronos2Forecaster(model_path="autogluon/chronos-2-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-2-synth": {
        "spec": (
            'Chronos2Forecaster(model_path="autogluon/chronos-2-synth", '
            'config={"device_map": "auto"})'
        )
    },
    # Chronos-Bolt.
    "chronos-bolt": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-tiny", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-bolt-mini": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-mini", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-bolt-small": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-bolt-base": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-bolt-base", '
            'config={"device_map": "auto"})'
        )
    },
    # Original Chronos (T5).
    "chronos-t5": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-tiny", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-t5-mini": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-mini", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-t5-small": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-small", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-t5-base": {
        "spec": (
            'ChronosForecaster(model_path="amazon/chronos-t5-base", '
            'config={"device_map": "auto"})'
        )
    },
    "chronos-t5-large": {
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
    "kronos-mini": {
        "spec": (
            'KronosForecaster(model_path="NeoQuasar/Kronos-mini", '
            'tokenizer_path="NeoQuasar/Kronos-Tokenizer-2k", deterministic=True)'
        )
    },
    "kronos-base": {
        "spec": (
            'KronosForecaster(model_path="NeoQuasar/Kronos-base", '
            'tokenizer_path="NeoQuasar/Kronos-Tokenizer-base", deterministic=True)'
        )
    },
    # Moirai 2.0 (small is the only published 2.0 size).
    "moirai-2": {
        "spec": 'Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")'
    },
    # TTM.
    "ttm": {"spec": 'TinyTimeMixerForecaster(fit_strategy="zero-shot")'},
    # TTM r1.
    "ttm-r1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm-r1-512-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'revision="main", fit_strategy="zero-shot")'
        )
    },
    "ttm-r1-1024-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r1", '
            'revision="1024_96_v1", fit_strategy="zero-shot")'
        )
    },
    # TTM r2.
    "ttm-r2": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-512-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="main", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-512-192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-512-336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-512-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-720-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1024-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-96-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1024-192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1024-336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1024-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1024-720-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1536-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-96-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1536-192": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-192-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1536-336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-336-r2", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2-1536-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="1536-720-r2", fit_strategy="zero-shot")'
        )
    },
    # TTM r2.1. Same Hub repo as r2, selected by revision.
    "ttm-r2.1-52-16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="52-16-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-52-16-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="52-16-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-90-30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="90-30-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-90-30-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="90-30-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-512-48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-48-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-512-48-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-48-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-512-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-96-ft-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-512-96-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="512-96-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-180-60-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="180-60-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    "ttm-r2.1-360-60-l1": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r2", '
            'revision="360-60-ft-l1-r2.1", fit_strategy="zero-shot")'
        )
    },
    # TTM r3.
    "ttm-r3": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-52-16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="52-16-dec-52-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-52-16-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="52-16-dec-52-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-90-30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="90-30-dec-90-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-90-30-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="90-30-dec-90-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-156-16": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="156-16-dec-52-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-156-16-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="156-16-dec-52-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-180-60": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="180-60-dec-180-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-180-60-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="180-60-dec-180-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-360-60": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="360-60-dec-360-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-360-60-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="360-60-dec-360-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-30": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-30-dec-90-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-30-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-30-dec-90-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-48-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-96-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-96-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-336": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-336-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-512-336-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="512-336-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-768-48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="768-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-768-48-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="768-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-48": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-48-dec-512-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-48-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-48-dec-512-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1024-720-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1024-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1536-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1536-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1536-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-1536-720-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="1536-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2048-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2048-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2048-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2048-720-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2048-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2560-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2560-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2560-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-2560-720-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="2560-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-3072-96": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-96-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-3072-96-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-96-lite-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-3072-720": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-720-r3", fit_strategy="zero-shot")'
        )
    },
    "ttm-r3-3072-720-lite": {
        "spec": (
            "TinyTimeMixerForecaster("
            'model_path="ibm-granite/granite-timeseries-ttm-r3", '
            'revision="3072-720-lite-r3", fit_strategy="zero-shot")'
        )
    },
    # TTM research r2. Ignored: runtime error (`index out of range in self`).
    # "ttm-research-r2-512-96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="main", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-512-192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-512-336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-512-720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="512-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1024-96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-96-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1024-192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1024-336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1024-720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1024-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1536-96": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-96-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1536-192": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-192-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1536-336": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-336-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # "ttm-research-r2-1536-720": {
    #     "spec": (
    #         "TinyTimeMixerForecaster("
    #         'model_path="ibm-research/ttm-research-r2", '
    #         'revision="1536-720-ft-r2", fit_strategy="zero-shot")'
    #     )
    # },
    # Time-MoE. Ignored: incompatible dependency pin (`transformers<=4.40.1`).
    # "timemoe-50m": {
    #     "spec": (
    #         'TimeMoEForecaster(model_path="Maple728/TimeMoE-50M", '
    #         'config={"device_map": "auto"})'
    #     )
    # },
    # "timemoe-200m": {
    #     "spec": (
    #         'TimeMoEForecaster(model_path="Maple728/TimeMoE-200M", '
    #         'config={"device_map": "auto"})'
    #     )
    # },
    # TiRex v1 requires an explicit license acceptance.
    "tirex": {"spec": 'TiRexForecaster(model="NX-AI/TiRex", license_accepted=True)'},
    "tirex-1.1-gifteval": {
        "spec": (
            'TiRexForecaster(model="NX-AI/TiRex-1.1-gifteval", license_accepted=True)'
        )
    },
    # TiRex-2. Ignored: not yet released in sktime.
    # "tirex-2": {
    #     "spec": 'TiRex2Forecaster(model_path="NX-AI/TiRex-2", device="auto")'
    # },
    # "tirex-2-gifteval-zs": {
    #     "spec": (
    #         'TiRex2Forecaster(model_path="NX-AI/TiRex-2-gifteval-zs", device="auto")'
    #     )
    # },
    # "tirex-2-gifteval-pretrain": {
    #     "spec": (
    #         'TiRex2Forecaster(model_path="NX-AI/TiRex-2-gifteval-pretrain", '
    #         'device="auto")'
    #     )
    # },
    # "tirex-2-fevbench": {
    #     "spec": 'TiRex2Forecaster(model_path="NX-AI/TiRex-2-fevbench", device="auto")'
    # },
    # MOIRAI 1.0 / 1.1. Salesforce safetensors path; map_location auto-picks device.
    "moirai-1.0-r-small": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-small", '
            'map_location="cpu")'
        )
    },
    "moirai-1.0-r-base": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-base", '
            'map_location="cpu")'
        )
    },
    "moirai-1.0-r-large": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.0-R-large", '
            'map_location="cpu")'
        )
    },
    "moirai-1.1-r-small": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.1-R-small", '
            'map_location="cpu")'
        )
    },
    "moirai-1.1-r-base": {
        "spec": (
            'MOIRAIForecaster(checkpoint_path="Salesforce/moirai-1.1-R-base", '
            'map_location="cpu")'
        )
    },
    "moirai-1.1-r-large": {
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
    "flowstate-granite": {
        "spec": (
            "FlowStateForecaster("
            'model_path="ibm-granite/granite-timeseries-flowstate-r1", '
            'revision="r1.1")'
        )
    },
    # TimesFM 2.x (transformers).
    "timesfm-2.5": {
        "spec": (
            'TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers", '
            'device_map="auto")'
        )
    },
    "timesfm-2": {
        "spec": (
            'TimesFM2Forecaster(model_path="google/timesfm-2.0-500m-pytorch", '
            'device_map="auto", forward_kwargs={"forecast_context_len": 1024})'
        )
    },
    # Toto 2.0 size grid.
    "toto-2.0-4m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-4m")'},
    "toto-2.0-22m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-22m")'},
    "toto-2.0-313m": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-313m")'},
    "toto-2.0-1b": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-1B")'},
    "toto-2.0-2.5b": {"spec": 'Toto2Forecaster(model_path="Datadog/Toto-2.0-2.5B")'},
    # Sundial. Ignored: incompatible dependency pin (`transformers[torch]~=4.40.0`).
    # "sundial": {"spec": 'SundialForecaster(model_path="thuml/sundial-base-128m")'},
    # Timer. Ignored: incompatible dependency pin (`python<3.13`).
    # "timer": {"spec": 'TimerForecaster(model_name="thuml/timer-base-84m")'},
    # Timer-S1. Ignored: incompatible dependency pin
    # (`transformers[torch]>4.57.0,<5.0.0`).
    # "timer-s1": {
    #     "spec": (
    #         'TimerS1Forecaster(model_path="bytedance-research/Timer-S1", '
    #         'device_map="auto", deterministic=True)'
    #     )
    # },
    # "timer-s1-4bit": {
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
    "windfm-robust": {
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
    # "patchtst-etth1": {
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
    # "cisctsm-preview": {
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
    "mantis-8m": {
        "spec": (
            'MantisForecaster(checkpoint="paris-noah/Mantis-8M", model_version="v1", '
            'device="auto", context_length=127)'
        )
    },
    "mantis-plus": {
        "spec": (
            'MantisForecaster(checkpoint="paris-noah/MantisPlus", model_version="v1", '
            'device="auto", context_length=127)'
        )
    },
    # Time-LLM. Ignored: runtime error (`selected index k out of range`).
    # "time-llm": {"spec": 'TimeLLMForecaster(llm_model="GPT2")'},
    # "time-llm-bert": {"spec": 'TimeLLMForecaster(llm_model="BERT")'},
    # "time-llm-llama": {"spec": 'TimeLLMForecaster(llm_model="LLAMA")'},
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
    elif model_id.startswith("chronos-2"):
        family = "chronos"
    elif model_id.startswith(("chronos-", "ttm", "timesfm-")):
        family = "hub"
    elif model_id.startswith(("kronos", "windfm")):
        family = "kronos"
    elif model_id.startswith("flowstate"):
        family = "granite"
    elif model_id.startswith(("moirai-", "lagllama")):
        family = "moirai"
    elif model_id.startswith("tirex"):
        family = "tirex"
    elif model_id.startswith("toto-"):
        family = "toto"
    elif model_id.startswith("mantis"):
        family = "mantis"
    else:
        raise KeyError(f"no group mapping for registry id {model_id!r}")
    return (family, "full")


for _id, _meta in SKTIME_REGISTRY.items():
    _meta["group"] = _group_for(_id)
