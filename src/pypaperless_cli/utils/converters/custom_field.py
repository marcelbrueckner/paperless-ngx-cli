"""Custom field related converter"""

import asyncio

from pypaperless.models.common import CustomFieldType

from typing import Any

from pypaperless_cli.api import PaperlessAsyncAPI
from pypaperless_cli.utils.validators.custom_field import _validate_custom_fields
from pypaperless_cli.utils.converters.helpers import strtobool

async def _get_custom_field_id(name: str) -> str:
    filters = {
        "name__iexact": name
    }
    async with PaperlessAsyncAPI() as paperless:
        async with paperless.custom_fields.reduce(**filters) as filtered:
            async for field in filtered:
                return field.id
            else:
                raise ValueError(f"Custom field \"{name}\" does not exist.")

async def _get_custom_field_type(id: int) -> CustomFieldType:
    """Returns CustomFieldType for a given custom field ID."""

    # Method will raise an error if the ID doesn't exist
    await _validate_custom_fields([id])

    # At this point, the custom field ID can be considered valid
    async with PaperlessAsyncAPI() as paperless:
        field = await paperless.custom_fields(id)
        return field.data_type

def custom_field_name_to_id(type_, *args) -> Any:
    """Determines ID for custom field name."""

    params = []

    for kv in args:
        k, *v = kv.split("=", maxsplit=1)

        if not k.isdigit():
            k = asyncio.run(_get_custom_field_id(k))

        # If no custom field value has been passed along (that is, a custom field ID or name isn't followed by an equal sign)
        # set the value to `None` so it can be distinguished later on
        # Ex.
        #   pngx document edit 123 --custom-fields 3=value 4= 5
        #   kv='3=value', k='3', v=['value']
        #   kv='4=', k='4', v=['']
        #   kv='5', k='5', v=[]
        if len(v) == 0:
            value = None
        else:
            value = "".join(v)
        
        if value and asyncio.run(_get_custom_field_type(int(k))) == CustomFieldType.BOOLEAN:
            value = strtobool(value)

        params.append({
            "id": int(k),
            "value": value
        })
    
    return params
