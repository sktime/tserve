import os

DEFAULT_PRELOAD = ["dummy", "chronos2", "timesfm2.5", "moirai2", "kronos"]


def preload_models() -> list[str]:
    raw = os.environ.get("FOMO_PRELOAD_MODELS")
    if raw is None:
        return DEFAULT_PRELOAD
    return [alias.strip() for alias in raw.split(",") if alias.strip()]
