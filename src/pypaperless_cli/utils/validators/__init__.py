"""Methods for value validation."""

from string import ascii_letters
from typing import Any


# Single value validation
from pypaperless_cli.utils.validators.document import document_exists

# List values validation
from pypaperless_cli.utils.validators.custom_field import custom_field_exists
from pypaperless_cli.utils.validators.tag import tag_exists


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

#
# Group validators
#

def adhoc_xor_specific(**kwargs):
    """Validate context selection isn't used together with any ad-hoc session parameter."""

    adhoc_session_params = ["host", "user", "password", "token"]

    if "use_context" in kwargs and any([True for p in kwargs.keys() if p in adhoc_session_params]):
        raise ValueError("Context selection (--use) may not be used together with ad-hoc session parameters.")
