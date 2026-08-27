"""sktime executor plugin (executor name ``sktime``).

Loads registry, zip, or in-process sktime forecasters. Domain mapping
onto ``(y, X, X_future, fh)`` is ``convertors`` (that spelling), not
the wire converters in ``fomo.types.converters``.

See Also
--------
fomo.runtime.executors.sktime.executor.SktimeExecutor
    Concrete ``Executor``.
fomo.runtime.executors.sktime.convertors
    Coerced request ↔ sktime fit/predict tables.
"""

from fomo.runtime.executors.sktime.executor import SktimeExecutor

__all__ = ["SktimeExecutor"]
