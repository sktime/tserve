import logging
from dataclasses import dataclass, field
from typing import Any

from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import resolve_model
from fomo.scheduling.scheduler import Scheduler
from fomo.types import ModelInfo, ModelsResult

logger = logging.getLogger(__name__)


@dataclass
class Runtime:
    executors: dict[str, Executor]
    scheduler: Scheduler
    models: dict[str, ModelInfo] = field(default_factory=dict)

    def loaded_models(self) -> ModelsResult:
        return ModelsResult(models=list(self.models.values()))


def bootstrap(load_models: list[Any]) -> Runtime:
    executors: dict[str, Executor] = {}
    models: dict[str, ModelInfo] = {}
    for model in load_models:
        info = resolve_model(model)
        if info.alias in models:
            raise ValueError(f"duplicate model alias {info.alias!r}")
        logger.info("loading model %s via %s", info.alias, info.executor)
        executor = create_executor(info.executor)
        executor.load(info, model)
        models[info.alias] = info
        executors[info.alias] = executor
    return Runtime(executors=executors, scheduler=Scheduler(executors), models=models)
