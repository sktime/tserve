"""pytorch-forecasting executor plugin (name ``pytorch-forecasting``).

The plugin is registered so ``create_executor`` can construct it.
Every ``Executor`` method currently raises ``NotImplementedError``.

See Also
--------
tserve.runtime.executors.pytorch_forecasting.executor.PytorchForecastingExecutor
    Stub implementation.
"""

from tserve.runtime.executors.pytorch_forecasting.executor import (
    PytorchForecastingExecutor,
)

__all__ = ["PytorchForecastingExecutor"]
