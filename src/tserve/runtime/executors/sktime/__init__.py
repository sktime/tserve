"""sktime executor plugin (executor name ``sktime``).

Loads registry, zip, or in-process sktime forecasters. Domain mapping
onto ``(y, X, X_future, fh)`` is ``tserve.runtime.executors.sktime.converters``,
not the wire converters in ``tserve.types.converters``.

See Also
--------
tserve.runtime.executors.sktime.executor.SktimeExecutor
    Concrete ``Executor``.
tserve.runtime.executors.sktime.converters
    Coerced request ↔ sktime fit/predict tables.
"""

from tserve.runtime.executors.sktime.executor import SktimeExecutor

__all__ = ["SktimeExecutor"]
