"""Tag related validators"""

import asyncio
from typing import Any, List

from pypaperless_cli.api import PaperlessAsyncAPI


async def _validate_tags(tag_ids: List[int]) -> None:
    """Validates tags by their IDs."""

    filters = {
        "id__in": ",".join(map(str,tag_ids))
    }

    async with PaperlessAsyncAPI() as paperless:
        async with paperless.tags.reduce(**filters) as filtered:
            existing_ids = await filtered.all()
    
    invalid_ids = set(tag_ids) - set(existing_ids)
    
    if len(invalid_ids) == 1:
        raise ValueError(f"Tag with ID {', '.join(map(str,invalid_ids))} does not exist.")
    if len(invalid_ids) > 1:
        raise ValueError(f"Tags with IDs {', '.join(map(str,invalid_ids))} do not exist.")


def tag_exists(type_, tags: List[int]) -> Any:
    """Validate tags exists."""
    
    asyncio.run(_validate_tags(tags))
