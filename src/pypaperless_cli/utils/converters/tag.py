"""Tag related converter"""

import asyncio
from typing import Any

from pypaperless_cli.api import PaperlessAsyncAPI


async def _get_tag_id(name: str) -> str:
    filters = {
        "name__iexact": name
    }
    async with PaperlessAsyncAPI() as paperless:
        async with paperless.tags.reduce(**filters) as filtered:
            async for tag in filtered:
                return tag.id
            else:
                raise ValueError(f"Tag \"{name}\" does not exist.")

def tag_name_to_id(type_, *args) -> Any:
    """Determines ID for tag name."""

    params = []

    for k in args:

        if not k.isdigit():
            k = asyncio.run(_get_tag_id(k))

        params.append(int(k))
    
    return params
