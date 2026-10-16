"""Custom field related validators"""

import asyncio
from typing import Any, List

from pypaperless.models.filters import CustomFieldFilters

from pypaperless_cli.api import PaperlessAsyncAPI


async def _validate_custom_fields(field_ids: List[int]) -> None:
    """Validates custom fields by their IDs."""

    filters: CustomFieldFilters = {
        "id__in": ",".join(map(str,field_ids))
    }

    async with PaperlessAsyncAPI() as paperless:
        async with paperless.custom_fields.filter(**filters) as filtered:
            existing_ids = [x.id for x in await filtered.as_list()]
    
    invalid_ids = set(field_ids) - set(existing_ids)
    
    if len(invalid_ids) == 1:
        raise ValueError(f"Custom field with ID {', '.join(map(str,invalid_ids))} does not exist.")
    if len(invalid_ids) > 1:
        raise ValueError(f"Custom fields with IDs {', '.join(map(str,invalid_ids))} do not exist.")
        

def custom_field_exists(type_, fields: List[dict]) -> Any:
    """Validate custom field exists."""
    
    field_ids = list(map(lambda f: f["id"], fields))
    asyncio.run(_validate_custom_fields(field_ids))
