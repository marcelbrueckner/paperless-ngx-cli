"""Command to manage documents."""

from cyclopts import App

from pypaperless_cli.utils import groups

from pypaperless_cli.commands.document.show import show
from pypaperless_cli.commands.document.edit import edit

document = App(name="document", help="Work with your documents.", group_commands=groups.commands, version_flags=[])
document["--help"].group = "Help"

document.command(show)
document.command(edit, group_arguments=groups.arguments, group_parameters=groups.standard_fields)
