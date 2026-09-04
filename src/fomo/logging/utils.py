def format_mib(mib: float) -> str:
    if mib >= 1024:
        return f"{mib / 1024:.2f} GB"
    return f"{mib:.0f} MB" if mib >= 10 else f"{mib:.1f} MB"
