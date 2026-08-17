from dataclasses import dataclass

from fomo.runtime.config import configured_models


@dataclass(frozen=True)
class ServerConfig:
    models: tuple[str, ...]
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"

    @classmethod
    def from_options(
        cls,
        *,
        models: list[str] | None = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> "ServerConfig":
        aliases = tuple(models) if models is not None else tuple(configured_models())
        return cls(models=aliases, host=host, port=port, log_level=log_level)
