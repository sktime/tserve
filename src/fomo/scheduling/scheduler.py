from fomo.runtime.executors import Executor
from fomo.types.models import ForecastRequest, ForecastResponse


class Scheduler:
    def __init__(self, executors: dict[str, Executor]) -> None:
        self._executors = executors

    def run(self, request: ForecastRequest) -> ForecastResponse:
        executor = self._executors.get(request.model)
        if executor is None:
            raise RuntimeError(f"model {request.model!r} is not loaded on this server")
        return executor.predict(request)
