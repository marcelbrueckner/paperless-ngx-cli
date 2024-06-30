"""
Command to manage documents.
"""

from typing import Annotated, Optional, Literal

from cyclopts import App, Parameter

from rich.console import Console
from rich.table import Table

from pypaperless_cli.const import GUI_PATH
from pypaperless_cli.config import config as appconfig
from pypaperless_cli.api import PaperlessAsyncAPI
from pypaperless_cli.utils import command_groups
from pypaperless_cli.utils.highlighter import highlight_none

document = App(name="document", help="Work with your documents", group_commands=command_groups.commands, version_flags=[])
document["--help"].group = "Help"

#
# DOCUMENT
#

@document.command
async def show(
    id: int, /, *,
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

    console = Console()

    async with PaperlessAsyncAPI() as paperless:
        document = await paperless.documents(id)
        doc_type = await paperless.document_types(document.document_type)
        correspondent = await paperless.correspondents(document.correspondent)
        storage_path = await paperless.storage_paths(document.storage_path)

        tags = []
        filters = {
            "id__in": ",".join(map(str, document.tags))
        }
        async with paperless.tags.reduce(**filters) as filtered:
            async for tag in filtered:
                tags.append(tag)

        custom_fields = []
        filters = {
            "id__in": ",".join(map(lambda f: str(f.field), document.custom_fields))
        }
        async with paperless.custom_fields.reduce(**filters) as filtered:
            async for field in filtered:
                custom_fields.append({
                    "id": field.id,
                    "name": field.name,
                    "value": next(x.value for x in document.custom_fields if x.field == field.id),
                    "data_type": field.data_type
                })

    if json:
        console.print_json(data=document._data)

    else:
        table = Table.grid(padding=(0,3))

        table.add_column(style="blue")
        table.add_column(style="green", no_wrap=True)

        table.add_row("[b]Title", f"[b]{highlight_none(document.title)}")
        table.add_row("ID", str(document.id))
        table.add_row("ASN", highlight_none(str(document.archive_serial_number)))
        table.add_row("Created", str(document.created_date))
        table.add_row("Correspondent", highlight_none(correspondent.name))
        table.add_row("Document type", highlight_none(doc_type.name))
        table.add_row("Storage path", f"{storage_path.name}\n({storage_path.path})")
        table.add_row("Tags", "\n".join([tag.name for tag in tags]))
        table.add_row("Details", f"{appconfig.current.host}{GUI_PATH["documents_details"].format(pk=document.id)}")

        table.add_row("[white]Custom fields")
        for custom_field in custom_fields:
            table.add_row(custom_field["name"], highlight_none(str(custom_field["value"])))

        console.print(table)

