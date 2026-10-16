"""Method for retrieving information about a document."""

from typing import Annotated, Any, Optional

from cyclopts import Parameter
from pypaperless.models.filters import CustomFieldFilters, TagFilters

from rich.console import Console
from rich.table import Table

from pypaperless_cli.api import PaperlessAsyncAPI
from pypaperless_cli.const import GUI_PATH
from pypaperless_cli.config import config as appconfig
from pypaperless_cli.utils.highlighter import highlight_none
from pypaperless_cli.utils.types import Document

async def show(
    id: Document, /, *,
    json: Annotated[Optional[bool], Parameter(
        negative = [],
        show_default = False
        )] = False,
    ) -> None:

    """Show information about a document.
    
    Parameters
    ----------
    id: int
        The ID of the document to show information about.
    json: bool
        If given, the information is printed as JSON.
    """

    async with PaperlessAsyncAPI() as paperless:
        document = await paperless.documents(id)
        
        # Everything except created date is optional
        # therefore initialize possibly empty fields
        doc_title = None
        doc_type = None
        correspondent = None
        storage_path = None
        tags = []
        custom_fields: list[dict[str, Any]] = []

        if document.title:
            doc_title = document.title

        if document.document_type is not None:
            _doc_type = await paperless.document_types(document.document_type)
            doc_type = _doc_type.name
        
        if document.correspondent is not None:
            _correspondent = await paperless.correspondents(document.correspondent)
            correspondent = _correspondent.name
        
        if document.storage_path is not None:
            _storage_path = await paperless.storage_paths(document.storage_path)
            storage_path = f"{_storage_path.name}\n({_storage_path.path})"

        
        if document.tags:
            tag_filters: TagFilters = {
                "id__in": ",".join(map(str, document.tags))
            }
            async with paperless.tags.filter(**tag_filters) as filtered_tags:
                async for tag in filtered_tags:
                    tags.append(tag)

        doc_custom_fields = list(document.custom_fields or [])
        if doc_custom_fields:
            custom_field_filters: CustomFieldFilters = {
                "id__in": ",".join(map(lambda f: str(f.field), doc_custom_fields))
            }
            async with paperless.custom_fields.filter(**custom_field_filters) as filtered_custom_fields:
                async for field in filtered_custom_fields:
                    custom_fields.append({
                        "id": field.id,
                        "name": field.name,
                        "value": next(x.value for x in doc_custom_fields if x.field == field.id),
                        "data_type": field.data_type
                    })

    if json:
        Console().print_json(data=document.model_dump(mode="json", by_alias=True))

    else:
        table = Table.grid(padding=(0,3))

        table.add_column(style="blue")
        table.add_column(style="green", no_wrap=True)

        # Explicitly check title as NoneHighlighter doesn't work well with additional styles
        if doc_title is not None:
            table.add_row("[b]Title", f"[b]{doc_title}")
        else:
            table.add_row("[b]Title", f"[b purple]{str(doc_title)}")

        table.add_row("ID", str(document.id))
        table.add_row("ASN", highlight_none(str(document.archive_serial_number)))
        table.add_row("Created", str(document.created))
        table.add_row("Correspondent", highlight_none(str(correspondent)))
        table.add_row("Document type", highlight_none(str(doc_type)))
        table.add_row("Storage path", highlight_none(str(storage_path)))

        if tags:
            table.add_row("Tags", "\n".join([tag.name for tag in tags]))
        else:
            table.add_row("Tags", highlight_none(str(None)))

        table.add_row("Details", f"{appconfig.current.host}{GUI_PATH['documents_details'].format(pk=document.id)}")

        table.add_row("[white]Custom fields")
        if custom_fields:
            for custom_field in custom_fields:
                table.add_row(custom_field["name"], highlight_none(str(custom_field["value"])))
        else:
            table.add_row(highlight_none(str(None)))

        Console().print(table)
