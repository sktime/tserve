"""Build a process-local ``Runtime`` by loading selected models.

FoMo is a time-series foundation-model inference server. Models load
once at process start via ``bootstrap``. This module does not dispatch
forecasts; that is ``fomo.scheduling.scheduler.Scheduler``.

See Also
--------
fomo.runtime.registry.resolve_model
    Turn a load-models item into ``ModelInfo``.
fomo.runtime.executors.create_executor
    Construct the plugin named by ``ModelInfo.executor``.
fomo.scheduling.scheduler.Scheduler
    Created here and stored on ``Runtime.scheduler``.
"""

import logging
import time
from pathlib import Path
from typing import Any

from fomo.logging import Stats
from fomo.logging.utils import format_mib, paint
from fomo.runtime.executors import Executor, create_executor
from fomo.runtime.registry import resolve_model
from fomo.scheduling.scheduler import Scheduler
from fomo.types import ModelInfo, ModelsResult

logger = logging.getLogger(__name__)


class Runtime:
    """Process-local handle: loaded executors, listing, stats, scheduler.

    ``GET /models`` reads ``loaded_models()``, which returns only models
    that ``bootstrap`` actually loaded. Registry catalog ids that were
    never passed to ``load_models`` / ``--load-models`` do not appear.

    Attributes
    ----------
    executors : dict of str to Executor
        Loaded model id → executor instance. Keys match ``ModelInfo.id``,
        not executor plugin names.
    scheduler : Scheduler
        Dispatch handle from ``fomo.scheduling`` (not this package).
    models : dict of str to ModelInfo
        Loaded model id → listing row (``id``, ``executor``, ``source``).
    stats : fomo.logging.Stats
        Load/warmup timings registered during bootstrap, plus later
        request stats recorded by the scheduler.
    """

    def __init__(
        self,
        executors: dict[str, Executor],
        scheduler: Scheduler,
        models: dict[str, ModelInfo] | None = None,
        stats: Stats | None = None,
    ) -> None:
        """Bind loaded handles. See the class docstring."""
        self.executors = executors
        self.scheduler = scheduler
        self.models = models if models is not None else {}
        self.stats = stats if stats is not None else Stats()

    def loaded_models(self) -> ModelsResult:
        """Return currently loaded models as a ``GET /models`` payload.

        Returns
        -------
        ModelsResult
            ``models`` is ``list(self.models.values())``, possibly empty.
        """
        return ModelsResult(models=list(self.models.values()))


def bootstrap(load_models: list[str | Path | tuple[str, Any]]) -> Runtime:
    """Resolve, construct, load, warmup, and register each selected model.

    For every item: ``resolve_model`` → ``create_executor(info.executor)``
    → ``load`` → ``warmup`` → ``stats.register``. Tuple items pass the
    second element (craft spec or object) to ``load``; strings and
    paths pass the item itself. Duplicate ``ModelInfo.id`` values raise
    before a second load.

    Parameters
    ----------
    load_models : list of str, Path, or (str, object)
        Items understood by ``resolve_model``: a registry id, a
        ``pathlib.Path`` to a ``.zip``, ``(id, craft spec)``, or
        ``(id, sktime BaseForecaster)``.

    Returns
    -------
    Runtime
        Executors and ``ModelInfo`` keyed by loaded id, a ``Stats``
        instance with load/warmup timings, and a ``Scheduler`` over
        those executors.

    Raises
    ------
    ValueError
        If two items resolve to the same ``ModelInfo.id``, or if
        ``resolve_model`` / ``create_executor`` raise ``ValueError``
        (unknown registry id, empty craft spec, non-zip path,
        unknown executor).
    TypeError
        If a tuple item is neither a craft spec string nor a
        sktime ``BaseForecaster`` (from ``resolve_model``).
    ImportError
        If ``create_executor`` cannot import the executor extra.

    Notes
    -----
    Executor ``load`` / ``warmup`` errors propagate unchanged
    (``NotImplementedError`` for ``pytorch-forecasting``).

    See Also
    --------
    fomo.scheduling.scheduler.Scheduler
        Forecast dispatch is not implemented in this package.
    """
    stats = Stats()
    executors: dict[str, Executor] = {}
    models: dict[str, ModelInfo] = {}

    total = len(load_models)
    plural = "" if total == 1 else "s"
    logger.info(f"Loading {paint(str(total), '1;36')} model{plural}")

    for position, item in enumerate(load_models, start=1):
        info = resolve_model(item)
        item = item[1] if isinstance(item, tuple) else item

        if info.id in models:
            raise ValueError(f"duplicate model id {info.id!r} in load_models")

        label = f"{info.id} via {info.executor}"
        dots = paint("." * max(3, 40 - len(label)), "2")
        prefix = (
            f"{paint(f'[{position}/{total}]', '2')} "
            f"{paint(info.id, '1;36')} via {paint(info.executor, '36')} "
            f"{dots} "
        )
        logger.info(prefix + paint("loading", "33"))

        executor = create_executor(info.executor)

        started = time.perf_counter()
        executor.load(info, item)
        load_s = time.perf_counter() - started

        started = time.perf_counter()
        executor.warmup()
        warmup_s = time.perf_counter() - started

        total_s = load_s + warmup_s
        logger.info(
            f"{prefix}{paint('ready', '32')} in "
            f"{paint(f'{total_s:.2f}s', '1;32')} "
            f"{paint(f'(load {load_s:.2f}s · warmup {warmup_s:.2f}s)', '2')}"
        )
        stats.register(info.id, info.executor, load_s, warmup_s)

        models[info.id] = info
        executors[info.id] = executor

    snapshot = stats.snapshot()
    memory = "".join(
        f" · {paint(probe, '2')} {paint(format_mib(mib), '36')}"
        for probe, mib in (
            ("CPU", snapshot["memory"]["cpu_rss_mb"]),
            ("GPU", snapshot["memory"]["gpu_mb"]),
        )
        if mib
    )
    elapsed = f"{snapshot['uptime_s']:.2f}s"
    logger.info(
        f"{paint(str(len(models)), '1;36')} model{plural} ready in "
        f"{paint(elapsed, '1;32')}{memory}\n"
    )

    return Runtime(
        executors=executors,
        scheduler=Scheduler(executors, stats),
        models=models,
        stats=stats,
    )
