import logging
import time
from typing import Any

from fomo.logging import Stats
from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import resolve_model
from fomo.scheduling.scheduler import Scheduler
from fomo.types import ModelInfo, ModelsResult

logger = logging.getLogger(__name__)


class Runtime:
    def __init__(
        self,
        executors: dict[str, Executor],
        scheduler: Scheduler,
        models: dict[str, ModelInfo] | None = None,
        stats: Stats | None = None,
    ) -> None:
        self.executors = executors
        self.scheduler = scheduler
        self.models = models if models is not None else {}
        self.stats = stats if stats is not None else Stats()

    def loaded_models(self) -> ModelsResult:
        return ModelsResult(models=list(self.models.values()))


def bootstrap(load_models: list[str | tuple[str, Any]]) -> Runtime:
    stats = Stats()
    executors: dict[str, Executor] = {}
    models: dict[str, ModelInfo] = {}

    for item in load_models:
        info = resolve_model(item)
        item = item[1] if isinstance(item, tuple) else item

        if info.id in models:
            raise ValueError(f"duplicate model id {info.id!r} in load_models")

        logger.info(f"loading model {info.id} via {info.executor}")
        executor = create_executor(info.executor)

        started = time.perf_counter()
        executor.load(info, item)
        load_s = time.perf_counter() - started

        started = time.perf_counter()
        executor.warmup()
        warmup_s = time.perf_counter() - started

        stats.register(info.id, info.executor, load_s, warmup_s)

        models[info.id] = info
        executors[info.id] = executor

    return Runtime(
        executors=executors,
        scheduler=Scheduler(executors, stats),
        models=models,
        stats=stats,
    )
