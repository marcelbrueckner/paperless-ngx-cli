"""Method for editing documents."""

from typing import Annotated, List, Optional

from cyclopts import Group, Parameter

from pypaperless_cli.api import PaperlessAsyncAPI
from pypaperless_cli.utils import converters, groups, validators

group_tags = Group(name = "Tags parameters", sort_key=groups.standard_fields.sort_key+1)

async def edit(
        id: int,
        /, *,
        asn: Optional[int] = None,
        correspondent: Optional[int] = None,
        document_type: Optional[int] = None,
        storage_path: Optional[int] = None,
        title: Optional[str] = None,
        created_date: Optional[str] = None,
        
        # Handle tags
        add_tags: Annotated[
            Optional[List[str|int]],
            Parameter(
                name = ["--tags", "--add-tags"],
                negative = [],
                group = group_tags,
                # Assigning converter/validator to custom type doesn't work with the current version of Cyclopts,
                # thus explicitly adding it to parameter
                converter = converters.tag_name_to_id,
                validator = validators.tag_exists
            )] = None,
        remove_tags: Annotated[
            Optional[List[str|int]],
            Parameter(
                negative = [],
                group = group_tags,
                # Assigning converter/validator to custom type doesn't work with the current version of Cyclopts,
                # thus explicitly adding it to parameter
                converter = converters.tag_name_to_id,
                validator = validators.tag_exists
            )] = None,
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

    add_tags: List[str|int]
        Assign tags. Requires the ID or the exact name of the tags.
    remove_tags: List[str|int]
        Unassign tags. Requires the ID or the exact name of the tags.
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

        if remove_tags:
            # Only keep tags not in `remove_tags``
            document.tags = [t for t in document.tags if t not in remove_tags]

        if add_tags:
            # Union existing and new tags, removing duplicate entries
            document.tags = list(dict.fromkeys(document.tags + add_tags))

        try:
            await document.update()
        except Exception as e:
            raise ValueError(str(e))
