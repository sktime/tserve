import importlib
import sys
import threading
import time
from collections.abc import Callable
from typing import Any


def _mb(n_bytes: int) -> float:
    return round(n_bytes / (1024 * 1024), 2)


def _probe(fn: Callable[[], float | None]) -> float | None:
    try:
        return fn()
    except Exception:
        return None


def _cpu_rss_mb() -> float | None:
    try:
        with open("/proc/self/status", encoding="utf-8") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    cpu_bytes = int(line.split()[1]) * 1024
                    return _mb(cpu_bytes)
    except Exception:
        pass
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
    def __init__(self) -> None:
        self.count = 0
        self.total = 0.0
        self.min: float | None = None
        self.max: float | None = None

    def add(self, seconds: float) -> None:
        self.count += 1
        self.total += seconds
        self.min = seconds if self.min is None else min(self.min, seconds)
        self.max = seconds if self.max is None else max(self.max, seconds)

    def as_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "total": self.total,
            "mean": self.total / self.count if self.count else None,
            "fastest": self.min,
            "slowest": self.max,
        }


class ModelStat:
    def __init__(
        self,
        executor: str,
        load_s: float | None,
        warmup_s: float | None,
    ) -> None:
        self.executor = executor
        self.load_s = load_s
        self.warmup_s = warmup_s
        self.requests_total = 0
        self.requests_ok = 0
        self.requests_failed = 0
        self.execute = Timing()

    def as_dict(self) -> dict[str, Any]:
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
    def __init__(self) -> None:
        self.started = time.perf_counter()
        self.models: dict[str, ModelStat] = {}
        self._lock = threading.Lock()

    def register(
        self,
        alias: str,
        executor: str,
        load_s: float | None,
        warmup_s: float | None,
    ) -> None:
        try:
            with self._lock:
                self.models[alias] = ModelStat(executor, load_s, warmup_s)
        except Exception:
            pass

    def record(self, alias: str, seconds: float, ok: bool) -> None:
        try:
            with self._lock:
                row = self.models.get(alias)
                if row is None:
                    return
                row.requests_total += 1
                if ok:
                    row.requests_ok += 1
                else:
                    row.requests_failed += 1
                row.execute.add(seconds)
        except Exception:
            pass

    def snapshot(self) -> dict[str, Any]:
        memory = {
            "cpu_rss_mb": _probe(_cpu_rss_mb),
            "gpu_mb": _probe(_gpu_mb),
        }
        with self._lock:
            models = {alias: row.as_dict() for alias, row in self.models.items()}
        return {
            "uptime_s": time.perf_counter() - self.started,
            "memory": memory,
            "models": models,
        }
