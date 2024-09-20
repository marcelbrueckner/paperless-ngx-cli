"""Document related validators"""

import asyncio
from typing import Any

from pypaperless_cli.api import PaperlessAsyncAPI


async def _validate_document(id: int) -> None:
    """Validates a document by its ID."""

    filters = {
        "id": id
    }

    async with PaperlessAsyncAPI() as paperless:
        async with paperless.documents.reduce(**filters) as filtered:
            documents = await filtered.all()

    if len(documents) == 0:
        raise ValueError(f"Document with ID {id} does not exist.")


def document_exists(type_, id: int) -> Any:
    """Validate document exists."""
    
    asyncio.run(_validate_document(id))
