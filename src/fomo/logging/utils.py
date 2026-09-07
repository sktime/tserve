"""Shared helpers for FoMo log lines."""

import sys


def paint(text: str, code: str) -> str:
    """Color ``text`` with an ANSI SGR ``code`` when stdout is a TTY.

    When ``sys.stdout.isatty()`` is true, the return value is
    ``text`` wrapped in ``\\033[<code>m`` … ``\\033[0m``. Otherwise
    ``text`` is returned unchanged so piped logs and CI stay plain.

    Codes used on FoMo log lines:

    * ``"1"`` — bold (banner title)
    * ``"2"`` — dim (counters, dots, breakdown, labels)
    * ``"32"`` / ``"1;32"`` — green / bold green (ready, elapsed)
    * ``"33"`` — yellow (loading)
    * ``"36"`` / ``"1;36"`` — cyan / bold cyan (ids, URLs, counts)

    Parameters
    ----------
    text : str
        Fragment to style. May be empty.
    code : str
        SGR parameter string, without the ``\\033[`` / ``m`` wrapper.
        Several attributes can be joined with ``;`` (for example
        ``"1;36"`` is bold + cyan).

    Returns
    -------
    str
        ``text`` with SGR prefix and reset when stdout is a terminal,
        else ``text`` as given.

    Examples
    --------
    On a terminal, cyan wraps the model id:

    >>> paint("naive", "36")  # doctest: +SKIP
    '\\x1b[36mnaive\\x1b[0m'

    Bold cyan for a count or URL:

    >>> paint("3", "1;36")  # doctest: +SKIP
    '\\x1b[1;36m3\\x1b[0m'

    Dim dots used as padding on the progress line:

    >>> paint("...", "2")  # doctest: +SKIP
    '\\x1b[2m...\\x1b[0m'

    When stdout is not a terminal (pipe, file, CI), every call is a
    no-op:

    >>> paint("naive", "36")  # doctest: +SKIP
    'naive'
    """
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def format_mib(mib: float) -> str:
    """Render a mebibyte value as a short ``MB`` or ``GB`` label.

    Used on the bootstrap summary line for CPU / GPU probes from
    ``Stats.snapshot``. Values at or above 1024 MiB are shown in
    gibibytes with two decimals. Smaller values stay in mebibytes:
    one decimal below 10 MiB, nearest integer from 10 MiB up.

    Parameters
    ----------
    mib : float
        Size in mebibytes (``bytes / 1024 ** 2``), as returned by
        ``Stats.snapshot()["memory"]``.

    Returns
    -------
    str
        A label such as ``"0.4 MB"``, ``"412 MB"``, or ``"1.80 GB"``.

    Examples
    --------
    Sub-10 MiB keeps one decimal:

    >>> format_mib(0.4)
    '0.4 MB'
    >>> format_mib(9.2)
    '9.2 MB'

    From 10 MiB, the value is rounded to an integer:

    >>> format_mib(41.7)
    '42 MB'
    >>> format_mib(412.0)
    '412 MB'

    1024 MiB and above switch to GB:

    >>> format_mib(1024.0)
    '1.00 GB'
    >>> format_mib(1843.2)
    '1.80 GB'
    """
    if mib >= 1024:
        return f"{mib / 1024:.2f} GB"
    return f"{mib:.0f} MB" if mib >= 10 else f"{mib:.1f} MB"
