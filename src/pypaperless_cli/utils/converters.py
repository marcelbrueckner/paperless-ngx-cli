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

def custom_field_name_to_id(type_, *args) -> Any:
    """Determines ID for custom field name."""

    params = []

    async def get_custom_field_id(name: str) -> str:
        filters = {
            "name__iexact": name
        }
        async with PaperlessAsyncAPI() as paperless:
            async with paperless.custom_fields.reduce(**filters) as filtered:
                async for field in filtered:
                    return field.id
                else:
                    raise ValueError(f"Custom field \"{name}\" does not exist.")

    for kv in args:
        k, *v = kv.split("=", maxsplit=1)

        if not k.isdigit():
            k = asyncio.run(get_custom_field_id(k))

        # If no custom field value has been passed along (that is, a custom field ID or name isn't followed by an equal sign)
        # set the value to `None` so it can be distinguished later on
        # Ex.
        #   poetry run pngx document edit 123 --custom-fields 3=value 4= 5
        #   kv='3=value', k='3', v=['value']
        #   kv='4=', k='4', v=['']
        #   kv='5', k='5', v=[]
        if len(v) == 0:
            value = None
        else:
            value = "".join(v)

        params.append({
            "id": int(k),
            "value": value
        })
    
    return params
