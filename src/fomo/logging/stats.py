"""In-memory, thread-safe metrics for loaded FoMo models.

FoMo is a time-series foundation-model inference server. ``Stats`` is
the process-local collector: ``bootstrap`` calls ``register`` after
each ``Executor.load`` and ``Executor.warmup``; ``Scheduler.run``
calls ``record`` for every predict attempt; ``GET /stats`` serializes
``snapshot()`` with ``StatsResult.model_validate``.

Dictionary keys under ``snapshot()["models"]`` are **loaded model
ids**, the same ids ``GET /models`` lists, not executor names such as
``"sktime"``. ``Timing.as_dict`` / ``ModelStat.as_dict`` keys match
the nested ``StatsResult`` schema (``count`` / ``total`` / ``mean`` /
``fastest`` / ``slowest``; ``requests`` ``total`` / ``ok`` /
``failed``; ``latency_s``).

``register`` and ``record`` wrap their bodies in
``contextlib.suppress(Exception)`` so metrics never break inference.
``_probe`` likewise returns ``None`` on any exception. There are no
custom exception classes; ``HealthError`` is an unrelated Pydantic
health payload.

This module does not convert frames. It does not call wire converters
(``fomo.types.converters``) or sktime converters
(``fomo.runtime.executors.sktime.converters``).

See Also
--------
fomo.types.models.StatsResult
    Schema ``GET /stats`` validates against the snapshot dict.
fomo.scheduling.scheduler.Scheduler
    Times ``Executor.predict`` and always calls ``record``.
"""

import contextlib
import importlib
import sys
import threading
import time
from collections.abc import Callable
from typing import Any


def _mb(n_bytes: int) -> float:
    """Convert a byte count to mebibytes, rounded to two decimals.

    Parameters
    ----------
    n_bytes : int
        Size in bytes.

    Returns
    -------
    float
        ``n_bytes / (1024 * 1024)`` rounded to two decimal places.
    """
    return round(n_bytes / (1024 * 1024), 2)


def _probe(fn: Callable[[], float | None]) -> float | None:
    """Call ``fn`` and return ``None`` on any exception.

    Used by ``Stats.snapshot`` so a failed memory probe cannot break
    ``GET /stats``.

    Parameters
    ----------
    fn : callable
        Zero-argument callable returning ``float`` or ``None``.

    Returns
    -------
    float or None
        ``fn()`` on success, or ``None`` if ``fn`` raises any
        ``Exception``.
    """
    try:
        return fn()
    except Exception:
        return None


def _cpu_rss_mb() -> float | None:
    """Read this process's resident set size in mebibytes.

    Prefers ``/proc/self/status`` ``VmRSS`` (kilobytes x 1024). If that
    path fails or has no ``VmRSS`` line, falls back to
    ``resource.getrusage(RUSAGE_SELF).ru_maxrss`` with a platform unit:
    Darwin treats ``ru_maxrss`` as bytes (x 1), Linux as kilobytes
    (x 1024). Any other platform returns ``None`` without calling
    ``resource``.

    Returns
    -------
    float or None
        RSS in MiB, or ``None`` if probing fails or the platform is
        neither Darwin nor Linux after the ``/proc`` path misses.
    """
    with (
        contextlib.suppress(Exception),
        open("/proc/self/status", encoding="utf-8") as status,
    ):
        for line in status:
            if line.startswith("VmRSS:"):
                cpu_bytes = int(line.split()[1]) * 1024
                return _mb(cpu_bytes)
    if sys.platform == "darwin":
        rss_unit_bytes = 1
    elif sys.platform.startswith("linux"):
        rss_unit_bytes = 1024
    else:
        return None
    try:
        resource = importlib.import_module("resource")
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        cpu_bytes = int(rss) * rss_unit_bytes
        return _mb(cpu_bytes)
    except Exception:
        return None


def _gpu_mb() -> float | None:
    """Sum CUDA ``memory_allocated`` across devices, in mebibytes.

    Looks up ``torch`` in ``sys.modules`` only. This function does not
    import torch itself, so a missing or broken CUDA driver cannot be
    triggered by stats collection. Returns ``None`` unless torch is
    already imported and ``torch.cuda.is_available()`` is true.

    Returns
    -------
    float or None
        Sum of ``torch.cuda.memory_allocated(i)`` over
        ``range(torch.cuda.device_count())``, converted with ``_mb``,
        or ``None`` if torch is absent, CUDA is unavailable, or any
        ``Exception`` is raised.
    """
    try:
        # avoid direct import for broken drivers/OS
        torch = sys.modules.get("torch")
        if torch is None:
            return None
        if not torch.cuda.is_available():
            return None
        used = sum(
            torch.cuda.memory_allocated(i) for i in range(torch.cuda.device_count())
        )
        return _mb(int(used))
    except Exception:
        return None


class Timing:
    """Accumulate wall-clock samples for one model's predict calls.

    ``as_dict`` keys match ``LatencySummary`` nested under
    ``StatsResult``: ``count``, ``total``, ``mean``, ``fastest``,
    ``slowest``. ``mean`` is ``total / count``, or ``None`` when
    ``count`` is 0. ``fastest`` / ``slowest`` are ``None`` until the
    first ``add``.

    Attributes
    ----------
    count : int
        Number of samples.
    total : float
        Sum of sample durations in seconds.
    min : float or None
        Fastest sample so far, or ``None`` if ``count`` is 0.
    max : float or None
        Slowest sample so far, or ``None`` if ``count`` is 0.
    """

    def __init__(self) -> None:
        """Initialize empty counters. See the class docstring."""
        self.count = 0
        self.total = 0.0
        self.min: float | None = None
        self.max: float | None = None

    def add(self, seconds: float) -> None:
        """Record one duration sample.

        Increments ``count``, adds ``seconds`` to ``total``, and updates
        ``min`` / ``max`` (first sample sets both).

        Parameters
        ----------
        seconds : float
            Wall time of one ``Scheduler.run`` predict attempt,
            including failed calls.
        """
        self.count += 1
        self.total += seconds
        self.min = seconds if self.min is None else min(self.min, seconds)
        self.max = seconds if self.max is None else max(self.max, seconds)

    def as_dict(self) -> dict[str, Any]:
        """Return the ``LatencySummary``-shaped dict.

        Returns
        -------
        dict
            ``count``, ``total``, ``mean`` (``None`` if ``count`` is
            0), ``fastest`` (``min``), ``slowest`` (``max``).
        """
        return {
            "count": self.count,
            "total": self.total,
            "mean": self.total / self.count if self.count else None,
            "fastest": self.min,
            "slowest": self.max,
        }


class ModelStat:
    """Hold load, warmup, and request metrics for one loaded model id.

    ``as_dict`` keys match ``ModelStats`` nested under
    ``StatsResult.models``: ``executor``, ``load_s``, ``warmup_s``,
    ``requests`` (``total`` / ``ok`` / ``failed``), ``latency_s``.

    Attributes
    ----------
    executor : str
        Executor plugin name recorded at register time (not the model
        id).
    load_s : float or None
        Wall time of ``Executor.load``.
    warmup_s : float or None
        Wall time of ``Executor.warmup``.
    requests_total : int
        ``ok + failed``.
    requests_ok : int
        Predict calls that returned without raising.
    requests_failed : int
        Predict calls that raised (still counted in ``execute``).
    execute : Timing
        Predict-call wall times, including failed calls.
    """

    def __init__(
        self,
        executor: str,
        load_s: float | None,
        warmup_s: float | None,
    ) -> None:
        """Store load metadata and zero request counters.

        See the class docstring for field meanings.

        Parameters
        ----------
        executor : str
            Executor plugin name (``"sktime"``,
            ``"pytorch-forecasting"``, ``"custom"``, …).
        load_s : float or None
            Wall time of ``Executor.load``.
        warmup_s : float or None
            Wall time of ``Executor.warmup``.
        """
        self.executor = executor
        self.load_s = load_s
        self.warmup_s = warmup_s
        self.requests_total = 0
        self.requests_ok = 0
        self.requests_failed = 0
        self.execute = Timing()

    def as_dict(self) -> dict[str, Any]:
        """Return the ``ModelStats``-shaped dict.

        Returns
        -------
        dict
            ``executor``, ``load_s``, ``warmup_s``, ``requests``
            (``total`` / ``ok`` / ``failed``), ``latency_s`` from
            ``Timing.as_dict``.
        """
        return {
            "executor": self.executor,
            "load_s": self.load_s,
            "warmup_s": self.warmup_s,
            "requests": {
                "total": self.requests_total,
                "ok": self.requests_ok,
                "failed": self.requests_failed,
            },
            "latency_s": self.execute.as_dict(),
        }


class Stats:
    """Collect in-memory, thread-safe inference metrics.

    A ``threading.Lock`` guards ``models``. ``register`` is called from
    bootstrap after load and warmup. ``record`` is called from
    ``Scheduler.run``. ``snapshot`` is what ``GET /stats`` serializes
    via ``StatsResult.model_validate``.

    ``register`` and ``record`` swallow every ``Exception`` so metrics
    never break inference. ``record`` is a no-op if ``id`` was never
    registered. Snapshot keys are loaded model ids, not executor names.

    Attributes
    ----------
    started : float
        ``time.perf_counter()`` at construction; ``snapshot`` reports
        ``uptime_s`` as now minus this value.
    models : dict of str to ModelStat
        Per **loaded model id** row.
    """

    def __init__(self) -> None:
        """Start the uptime clock and an empty model map.

        See the class docstring.
        """
        self.started = time.perf_counter()
        self.models: dict[str, ModelStat] = {}
        self._lock = threading.Lock()

    def register(
        self,
        id: str,
        executor: str,
        load_s: float | None,
        warmup_s: float | None,
    ) -> None:
        """Store a ``ModelStat`` for a loaded model id.

        Called from bootstrap after ``Executor.load`` and
        ``Executor.warmup``. Replaces any existing row for ``id``.
        Failures are swallowed (``contextlib.suppress(Exception)``).

        Parameters
        ----------
        id : str
            Loaded model id (not an executor name).
        executor : str
            Executor plugin name recorded on the row.
        load_s : float or None
            Wall time of ``Executor.load``.
        warmup_s : float or None
            Wall time of ``Executor.warmup``.
        """
        with contextlib.suppress(Exception), self._lock:
            self.models[id] = ModelStat(executor, load_s, warmup_s)

    def record(self, id: str, seconds: float, ok: bool) -> None:
        """Count one predict attempt and add its latency.

        Called from ``Scheduler.run``. Increments ``requests_total``,
        then ``requests_ok`` or ``requests_failed``, and ``execute.add``.
        Unknown ``id`` returns without changing state. Failures are
        swallowed (``contextlib.suppress(Exception)``).

        Parameters
        ----------
        id : str
            Loaded model id used as the ``models`` key.
        seconds : float
            Wall time of the predict call (success or failure).
        ok : bool
            ``True`` if ``Executor.predict`` returned; ``False`` if it
            raised.
        """
        with contextlib.suppress(Exception), self._lock:
            row = self.models.get(id)
            if row is None:
                return
            row.requests_total += 1
            if ok:
                row.requests_ok += 1
            else:
                row.requests_failed += 1
            row.execute.add(seconds)

    def snapshot(self) -> dict[str, Any]:
        """Return the dict ``GET /stats`` validates as ``StatsResult``.

        Memory probes run outside the lock via ``_probe``. The
        ``models`` copy is taken under the lock.

        Returns
        -------
        dict
            ``uptime_s`` (seconds since construction), ``memory``
            (``cpu_rss_mb``, ``gpu_mb``, each possibly ``None``), and
            ``models`` mapping loaded model id → ``ModelStat.as_dict``.
        """
        memory = {
            "cpu_rss_mb": _probe(_cpu_rss_mb),
            "gpu_mb": _probe(_gpu_mb),
        }
        with self._lock:
            models = {model_id: row.as_dict() for model_id, row in self.models.items()}
        return {
            "uptime_s": time.perf_counter() - self.started,
            "memory": memory,
            "models": models,
        }
