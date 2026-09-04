import sys


def paint(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def format_mib(mib: float) -> str:
    if mib >= 1024:
        return f"{mib / 1024:.2f} GB"
    return f"{mib:.0f} MB" if mib >= 10 else f"{mib:.1f} MB"
