from fomo.types import ModelInfo, ModelsResult

MODELS = ModelsResult(
    models=[
        ModelInfo(
            alias="dummy",
            estimator="NaiveForecaster",
            executor="sktime",
            multivariate=False,
            exogenous=False,
            quantiles=True,
            spec="NaiveForecaster()",
        ),
        ModelInfo(
            alias="chronos2",
            estimator="Chronos2Forecaster",
            executor="sktime",
            multivariate=True,
            exogenous=True,
            quantiles=False,
            spec='Chronos2Forecaster(model_path="amazon/chronos-2")',
        ),
        ModelInfo(
            alias="timesfm2.5",
            estimator="TimesFM2Forecaster",
            executor="sktime",
            multivariate=False,
            exogenous=False,
            quantiles=False,
            spec='TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers")',
        ),
        ModelInfo(
            alias="moirai2",
            estimator="Moirai2Forecaster",
            executor="sktime",
            multivariate=True,
            exogenous=False,
            quantiles=False,
            spec='Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")',
        ),
        ModelInfo(
            alias="kronos",
            estimator="KronosForecaster",
            executor="sktime",
            multivariate=False,
            exogenous=False,
            quantiles=False,
            spec='KronosForecaster(model_path="NeoQuasar/Kronos-small")',
        ),
    ]
)


def get_model(alias: str) -> ModelInfo:
    for model in MODELS.models:
        if model.alias == alias:
            return model
    known = ", ".join(model.alias for model in MODELS.models)
    raise ValueError(f"unknown model {alias!r}, choose one of: {known}")
