"""Method for editing documents."""

from typing import Optional

from pypaperless_cli.api import PaperlessAsyncAPI

async def edit(
        id: int,
        /, *,
        asn: Optional[int] = None,
        correspondent: Optional[int] = None,
        document_type: Optional[int] = None,
        storage_path: Optional[int] = None,
        title: Optional[str] = None,
        created_date: Optional[str] = None,
    ) -> None:

    """Update a document's information.
    
    Parameters
    ----------
    id: int
        The ID of the document to be updated.
    asn: int
        Archive serial number. The unique identifier of the document in your physical document binders.
    correspondent: int
        ID of the correspondent.
    document_type: int
        ID of the document type.
    storage_path: int
        ID of the storage path.
    title: str
        Document title
    created_date: str
        The ISO 8601 date (YYYY-MM-DD) the document was initially issued.
    """

    async with PaperlessAsyncAPI() as paperless:
        document = await paperless.documents(id)

        if asn:
            document.archive_serial_number = asn
        
        if correspondent:
            document.correspondent = correspondent
        
        if document_type:
            document.document_type = document_type
        
        if storage_path:
            document.storage_path = storage_path
        
        if title:
            document.title = title
        
        if created_date:
            document.created_date = created_date

        try:
            await document.update()
        except Exception as e:
            raise ValueError(str(e))
