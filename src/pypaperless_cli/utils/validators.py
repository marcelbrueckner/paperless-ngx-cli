"""
Validators.
"""

import asyncio
from string import ascii_letters
from typing import Any, List

from pypaperless_cli.api import PaperlessAsyncAPI


#
# Parameter validators
#

def not_empty(type_, value: Any) -> None:
    if not value:
        raise ValueError("Must not be empty.")

def starts_with_ascii_letters(type_, value: str) -> None:
    if not value.startswith(tuple(ascii_letters)):
        raise ValueError("Must start with a letter.")

def url(type_, value) -> None:
    valid_protocols = ('http://', 'https://')
    if not value.startswith(valid_protocols):
        raise ValueError(f"Must start with {valid_protocols}.")

def tag_exists(type_, tags: List[int]) -> Any:
    """Validate tag exists."""

    async def validate_tag_id(tag_ids: List[int]) -> None:
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
    
    asyncio.run(validate_tag_id(tags))

#
# Group validators
#

def adhoc_xor_specific(**kwargs):
    """Validate context selection isn't used together with any ad-hoc session parameter."""

    adhoc_session_params = ["host", "user", "password", "token"]

    if "use_context" in kwargs and any([True for p in kwargs.keys() if p in adhoc_session_params]):
        raise ValueError("Context selection (--use) may not be used together with ad-hoc session parameters.")
