import time

from fomo.logging import Stats
from fomo.runtime.executors import Executor
from fomo.types.models import CoercedForecastRequest, CoercedForecastResponse


class Scheduler:
    def __init__(self, executors: dict[str, Executor], stats: Stats) -> None:
        self._executors = executors
        self._stats = stats

    def run(self, request: CoercedForecastRequest) -> CoercedForecastResponse:
        executor = self._executors.get(request.model)
        if executor is None:
            raise RuntimeError(f"model {request.model!r} is not loaded on the server")

        started = time.perf_counter()
        ok = False
        try:
            response = executor.predict(request)
            ok = True
            return response
        finally:
            self._stats.record(request.model, time.perf_counter() - started, ok)
