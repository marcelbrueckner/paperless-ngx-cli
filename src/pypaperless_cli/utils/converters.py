"""
Converters.
"""

import asyncio
from typing import Any

from pypaperless_cli.api import PaperlessAsyncAPI


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

def tag_name_to_id(type_, *args) -> Any:
    """Determines ID for tag name."""

    params = []

    async def get_tag_id(name: str) -> str:
        filters = {
            "name__iexact": name
        }
        async with PaperlessAsyncAPI() as paperless:
            async with paperless.tags.reduce(**filters) as filtered:
                async for tag in filtered:
                    return tag.id
                else:
                    raise ValueError(f"Tag \"{name}\" does not exist.")

    for k in args:

        if not k.isdigit():
            k = asyncio.run(get_tag_id(k))

        params.append(int(k))
    
    return params

