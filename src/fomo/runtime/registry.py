from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    alias: str
    estimator: str
    spec: str
    multivariate: bool = False
    exogenous: bool = False
    quantiles: bool = False


MODELS: dict[str, ModelSpec] = {
    "dummy": ModelSpec(
        alias="dummy",
        estimator="NaiveForecaster",
        spec="NaiveForecaster()",
        quantiles=True,
    ),
    "chronos2": ModelSpec(
        alias="chronos2",
        estimator="Chronos2Forecaster",
        spec='Chronos2Forecaster(model_path="amazon/chronos-2")',
        multivariate=True,
        exogenous=True,
    ),
    "timesfm2.5": ModelSpec(
        alias="timesfm2.5",
        estimator="TimesFM2Forecaster",
        spec='TimesFM2Forecaster(model_path="google/timesfm-2.5-200m-transformers")',
    ),
    "moirai2": ModelSpec(
        alias="moirai2",
        estimator="Moirai2Forecaster",
        spec='Moirai2Forecaster(checkpoint_path="Salesforce/moirai-2.0-R-small")',
        multivariate=True,
    ),
    "kronos": ModelSpec(
        alias="kronos",
        estimator="KronosForecaster",
        spec='KronosForecaster(model_path="NeoQuasar/Kronos-small")',
    ),
}


def get_model(alias: str) -> ModelSpec:
    try:
        return MODELS[alias]
    except KeyError as exc:
        known = ", ".join(sorted(MODELS))
        raise ValueError(f"unknown model {alias!r}, choose one of: {known}") from exc
