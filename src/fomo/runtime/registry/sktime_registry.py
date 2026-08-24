from fomo.runtime.registry import BASE_REGISTRY_TYPE

# Catalog of ids the server can load. Nothing here is loaded until
# --load-models / load_models selects it.
# Checkout https://github.com/sktime/fomo/issues/1
# Each spec is an import path plus constructor kwargs; ModelInfo is listing-only.
SKTIME_REGISTRY: BASE_REGISTRY_TYPE = {
    "naive": {
        "spec": {
            "class": "sktime.forecasting.naive.NaiveForecaster",
            "kwargs": {},
        },
    },
    "chronos-2": {
        "spec": {
            "class": "sktime.forecasting.chronos2.Chronos2Forecaster",
            "kwargs": {
                "model_path": "amazon/chronos-2",
                "config": {"device_map": "auto"},
            },
        },
    },
    "chronos": {
        "spec": {
            "class": "sktime.forecasting.chronos.ChronosForecaster",
            "kwargs": {
                "model_path": "amazon/chronos-bolt-tiny",
                "config": {"device_map": "auto"},
            },
        },
    },
    "kronos": {
        "spec": {
            "class": "sktime.forecasting.kronos.KronosForecaster",
            "kwargs": {"model_path": "NeoQuasar/Kronos-small"},
        },
    },
    "moirai-2": {
        "spec": {
            "class": "sktime.forecasting.moirai2.Moirai2Forecaster",
            "kwargs": {"checkpoint_path": "Salesforce/moirai-2.0-R-small"},
        },
    },
    "ttm": {
        "spec": {
            "class": "sktime.forecasting.ttm.TinyTimeMixerForecaster",
            "kwargs": {"model_path": "ibm-granite/granite-timeseries-ttm-r2"},
        },
    },
    "momentfm": {
        "spec": {
            "class": "sktime.detection.momentfm.MomentFMAnomalyDetector",
            "kwargs": {
                "pretrained_model_name_or_path": "AutonLab/MOMENT-1-small",
                "device": "auto",
            },
        },
    },
    "timemoe": {
        "spec": {
            "class": "sktime.forecasting.timemoe.TimeMoEForecaster",
            "kwargs": {
                "model_path": "Maple728/TimeMoE-50M",
                "config": {"device_map": "auto"},
            },
        },
    },
    "tirex": {
        "spec": {
            "class": "sktime.forecasting.tirex.TiRexForecaster",
            "kwargs": {"model": "NX-AI/TiRex"},
        },
    },
    "moirai": {
        "spec": {
            "class": "sktime.forecasting.moirai.MOIRAIForecaster",
            "kwargs": {
                "checkpoint_path": "Salesforce/moirai-1.0-R-small",
                "map_location": "auto",
            },
        },
    },
    "toto": {
        "spec": {
            "class": "sktime.forecasting.toto.TotoForecaster",
            "kwargs": {"model_path": "Datadog/Toto-Open-Base-1.0"},
        },
    },
    "flowstate": {
        "spec": {
            "class": "sktime.forecasting.flowstate.FlowStateForecaster",
            "kwargs": {"model_path": "ibm-research/flowstate"},
        },
    },
    "tspulse": {
        "spec": {
            "class": "sktime.detection.tspulse.TSPulseAnomalyDetector",
            "kwargs": {"model_path": "ibm-granite/granite-timeseries-tspulse-r1"},
        },
    },
    "timesfm-2.5": {
        "spec": {
            "class": "sktime.forecasting.timesfm2.TimesFM2Forecaster",
            "kwargs": {
                "model_path": "google/timesfm-2.5-200m-transformers",
                "device_map": "auto",
            },
        },
    },
    "toto-2": {
        "spec": {
            "class": "sktime.forecasting.toto2.Toto2Forecaster",
            "kwargs": {"model_path": "Datadog/Toto-2.0-22m"},
        },
    },
    "sundial": {
        "spec": {
            "class": "sktime.forecasting.sundial.SundialForecaster",
            "kwargs": {"model_path": "thuml/sundial-base-128m"},
        },
    },
    "timer": {
        "spec": {
            "class": "sktime.forecasting.timer.TimerForecaster",
            "kwargs": {"model_name": "thuml/timer-base-84m"},
        },
    },
    "patchtsmixer": {
        "spec": {
            "class": "sktime.forecasting.patch_tsmixer.PatchTSMixerForecaster",
            "kwargs": {"model_path": "ibm-granite/granite-timeseries-patchtsmixer"},
        },
    },
    "falcontst": {
        "spec": {
            "class": "sktime.forecasting.falcon_tst.FalconTSTForecaster",
            "kwargs": {
                "model_path": "ant-intl/Falcon-TST_Large",
                "device_map": "auto",
            },
        },
    },
    "timer-s1": {
        "spec": {
            "class": "sktime.forecasting.timer_s1.TimerS1Forecaster",
            "kwargs": {
                "model_path": "bytedance-research/Timer-S1",
                "device_map": "auto",
            },
        },
    },
    "windfm": {
        "spec": {
            "class": "sktime.forecasting.windfm.WindFMForecaster",
            "kwargs": {"model_path": "NeoQuasar/WindFM"},
        },
    },
    "mira": {
        "spec": {
            "class": "sktime.forecasting.mira.MIRAForecaster",
            "kwargs": {"model_path": "MIRA-Mode/MIRA"},
        },
    },
    "patchtst": {
        "spec": {
            "class": "sktime.forecasting.patch_tst.PatchTSTForecaster",
            "kwargs": {"model_path": "namctin/patchtst_etth1_forecast"},
        },
    },
    "cisctsm": {
        "spec": {
            "class": "sktime.forecasting.cisco_tsm.CiscoTSMForecaster",
            "kwargs": {
                "model_path": "cisco-ai/cisco-time-series-model-1.0-preview",
                "backend": "gpu",
            },
        },
    },
    "timesfm": {
        "spec": {
            "class": "sktime.forecasting.timesfm.TimesFMForecaster",
            "kwargs": {"repo_id": "google/timesfm-1.0-200m"},
        },
    },
    "aurora": {
        "spec": {
            "class": "sktime.forecasting.aurora.AuroraForecaster",
            "kwargs": {"repo_id": "DecisionIntelligence/Aurora"},
        },
    },
    "lagllama": {
        "spec": {
            "class": "sktime.forecasting.lagllama.LagLlamaForecaster",
            "kwargs": {"ckpt_path": "time-series-foundation-models/Lag-Llama"},
        },
    },
    "falconx": {
        "spec": {
            "class": "sktime.forecasting.falcon_x.FalconXForecaster",
            "kwargs": {},
        },
    },
}
