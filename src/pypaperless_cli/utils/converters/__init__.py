"""Methods for type conversion"""

from typing import Any


from pypaperless_cli.utils.converters.custom_field import custom_field_name_to_id
from pypaperless_cli.utils.converters.tag import tag_name_to_id

import pypaperless_cli.utils.converters.helpers

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
