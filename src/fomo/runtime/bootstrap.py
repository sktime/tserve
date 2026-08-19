import logging
from dataclasses import dataclass

from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import get_model
from fomo.scheduling.scheduler import Scheduler

logger = logging.getLogger(__name__)


@dataclass
class Runtime:
    executors: dict[str, Executor]
    scheduler: Scheduler


def bootstrap(load_models: list[str] | None = None) -> Runtime:
    executors: dict[str, Executor] = {}
    for alias in load_models or []:
        spec = get_model(alias)
        logger.info("loading model %s via %s", alias, spec.executor)
        executor = create_executor(spec.executor)
        executor.load(spec)
        executors[alias] = executor
    return Runtime(executors=executors, scheduler=Scheduler(executors))
