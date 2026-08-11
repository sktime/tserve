import logging
from dataclasses import dataclass

from fomo.runtime.config import preload_models
from fomo.runtime.executor import Executor
from fomo.scheduling.scheduler import Scheduler

logger = logging.getLogger(__name__)


@dataclass
class Runtime:
    executor: Executor
    scheduler: Scheduler


def bootstrap(preload: list[str] | None = None) -> Runtime:
    executor = Executor()
    for alias in preload if preload is not None else preload_models():
        logger.info("loading model %s", alias)
        executor.load(alias)
    return Runtime(executor=executor, scheduler=Scheduler(executor))
