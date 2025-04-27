"""Method for editing documents."""

from typing import Annotated, List, Optional

from cyclopts import Group, Parameter

from pypaperless_cli.api import PaperlessAsyncAPI
from pypaperless_cli.utils import converters, groups, validators
from pypaperless_cli.utils.types import CustomFieldKeyValue, Document

group_tags = Group(name = "Tags parameters", sort_key=groups.standard_fields.sort_key+1)
group_custom_fields = Group(name = "Custom fields parameters", sort_key=group_tags.sort_key+1)

async def edit(
    id: Document,
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

    add_custom_fields: Annotated[
        Optional[List[CustomFieldKeyValue]],
        Parameter(
            name = ["--custom-fields", "--add-custom-fields"],
            negative = [],
            group = group_custom_fields,
            # Assigning converter/validator to custom type doesn't work with the current version of Cyclopts,
            # thus explicitly adding it to parameter
            converter = converters.custom_field_name_to_id,
            validator = validators.custom_field_exists
        )] = None,
    remove_custom_fields: Annotated[
        Optional[List[CustomFieldKeyValue]],
        Parameter(
            negative = [],
            group = group_custom_fields,
            # Assigning converter/validator to custom type doesn't work with the current version of Cyclopts,
            # thus explicitly adding it to parameter
            converter = converters.custom_field_name_to_id,
            validator = validators.custom_field_exists
        )] = None
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

    add_custom_fields: List[CustomFieldKeyValue]
        Assign custom fields (--custom-fields <NAME|ID>), optionally set a value (--custom-fields <NAME|ID>=VALUE).
        To clear a custom field, set VALUE to an empty string.
    remove_custom_fields: List[CustomFieldKeyValue]
        Unassign given custom fields.
    """

    async with PaperlessAsyncAPI() as paperless:
        # Define how document should be updated
        only_changed: bool = True
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
            from datetime import datetime
            document.created = datetime.strptime(created_date, "%Y-%m-%d")

        if remove_tags:
            # Only keep tags not in `remove_tags``
            document.tags = [t for t in document.tags if t not in remove_tags]

        if add_tags:
            # Union existing and new tags, removing duplicate entries
            document.tags = list(dict.fromkeys(document.tags + add_tags))

        if remove_custom_fields:
            # Remove given custom field if it's assigned to document
            for f in remove_custom_fields:
                remove_custom_field = next((custom_field for custom_field in document.custom_fields._data if custom_field["field"] == f["id"]), None)
                if remove_custom_field:
                    document.custom_fields._data.remove(remove_custom_field)

            # Custom fields are only updated by paperless-api when updating all fields (PUT)
            only_changed = False

        if add_custom_fields:
            # Update existing custom fields with possibly new values
            for custom_field in document.custom_fields._data:
                updated_custom_field = next((f for f in add_custom_fields if custom_field["field"] == f["id"]), None)
                if updated_custom_field:
                    if updated_custom_field["value"] is not None:
                        custom_field["value"] = updated_custom_field["value"]
                    add_custom_fields.remove(updated_custom_field)
            
            # Add remaining new custom fields
            for custom_field in add_custom_fields:
                new_custom_field = {
                    "field": custom_field["id"],
                    "value": custom_field["value"]
                }
                document.custom_fields._data.append(new_custom_field)
            
            # Custom fields are only updated by paperless-api when updating all fields (PUT)
            only_changed = False

        try:
            await document.update(only_changed=only_changed)
        except Exception as e:
            raise ValueError(str(e))
