"""Custom variable types."""

from typing import Annotated

from cyclopts import Parameter

from pypaperless_cli.utils import converters, validators


account_alias = Annotated[str, Parameter(
    show_default = False,
    validator = validators.starts_with_ascii_letters
    )]

URL = Annotated[str, Parameter(
    converter = converters.format_url,
    validator = [validators.not_empty, validators.url]
    )]
