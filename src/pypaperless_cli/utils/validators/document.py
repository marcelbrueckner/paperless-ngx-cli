"""Document related validators"""

import asyncio
from typing import Any

from pypaperless.models.filters import DocumentFilters

from pypaperless_cli.api import PaperlessAsyncAPI


async def _validate_document(id: int) -> None:
    """Validates a document by its ID."""

    filters: DocumentFilters = {
        "id": id
    }

    async with PaperlessAsyncAPI() as paperless:
        async with paperless.documents.filter(**filters) as filtered:
            documents = [x.id for x in await filtered.as_list()]

    if len(documents) == 0:
        raise ValueError(f"Document with ID {id} does not exist.")


def document_exists(type_, id: int) -> Any:
    """Validate document exists."""
    
    asyncio.run(_validate_document(id))
