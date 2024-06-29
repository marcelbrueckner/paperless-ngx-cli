"""
Converters.
"""

from typing import Any


def format_url(type_, *args) -> Any:
    """Default to https:// for URLs without scheme."""

    value = args[0]
    value = value.rstrip("/")

    if "://" not in value:
        return f"https://{value}"
    else:
        # If it's not a valid scheme,
        # subsequent validation will catch any error
        return value
