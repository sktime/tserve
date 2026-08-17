import os

DEFAULT_MODELS = ["dummy", "chronos2", "timesfm2.5", "moirai2", "kronos"]


def configured_models() -> list[str]:
    raw = os.environ.get("FOMO_MODELS")
    if raw is None:
        return DEFAULT_MODELS
    return [alias.strip() for alias in raw.split(",") if alias.strip()]
