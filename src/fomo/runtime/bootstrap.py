import logging
from dataclasses import dataclass

from fomo.runtime.config import configured_models
from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import get_model
from fomo.scheduling.scheduler import Scheduler

logger = logging.getLogger(__name__)


@dataclass
class Runtime:
    executors: dict[str, Executor]
    scheduler: Scheduler

    def health(self) -> dict:
        return {
            "status": "ok",
            "loaded_models": sorted(self.executors),
            "executors": {
                alias: get_model(alias).executor for alias in self.executors
            },
        }


def bootstrap(models: list[str] | None = None) -> Runtime:
    executors: dict[str, Executor] = {}
    for alias in models if models is not None else configured_models():
        spec = get_model(alias)
        logger.info("loading model %s via %s", alias, spec.executor)
        executor = create_executor(spec.executor)
        executor.load(spec)
        executors[alias] = executor
    return Runtime(executors=executors, scheduler=Scheduler(executors))
