import logging
from dataclasses import dataclass, field

from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import resolve_spec
from fomo.scheduling.scheduler import Scheduler
from fomo.types import ModelInfo

logger = logging.getLogger(__name__)


@dataclass
class Runtime:
    executors: dict[str, Executor]
    scheduler: Scheduler
    models: dict[str, ModelInfo] = field(default_factory=dict)


def bootstrap(load_models: list[str | ModelInfo] | None = None) -> Runtime:
    executors: dict[str, Executor] = {}
    models: dict[str, ModelInfo] = {}
    for item in load_models or []:
        spec = resolve_spec(item)
        if spec.alias in models:
            raise ValueError(f"duplicate model alias {spec.alias!r}")
        logger.info("loading model %s via %s", spec.alias, spec.executor)
        executor = create_executor(spec.executor)
        executor.load(spec)
        models[spec.alias] = spec
        executors[spec.alias] = executor
    return Runtime(executors=executors, scheduler=Scheduler(executors), models=models)
