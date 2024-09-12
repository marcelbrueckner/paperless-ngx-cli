#!/usr/bin/env python

import sys
from typing import Annotated, Optional

from cyclopts import App, Parameter
from cyclopts.types import Path
from cyclopts.exceptions import format_cyclopts_error

from rich.prompt import Prompt
from rich.console import Console

from pypaperless_cli.config import config as appconfig
from pypaperless_cli.utils import groups, validators
from pypaperless_cli.commands import (
    auth,
    document,
)
from pypaperless_cli.utils.types import (
    account_alias,
    URL
)


# BASIC APP STRUCTURE
# Loosely based on the Paperless-ngx API and web interface structure
# https://cyclopts.readthedocs.io/en/latest/commands.html
# https://docs.paperless-ngx.com/api/

app = App(
        name="pngx",
        help="Command-line interface for Paperless-ngx 🌱",
        group_commands=groups.commands,
        version_flags=["--version", "-v"]
    )

# Change the group of "--help" and "--version" to the implicit "Help" group.
app["--help"].group = "Help"
app["--version"].group = "Help"

app.command(auth)
app.command(document)


#
# CLI HELP
#

app.meta["--help"].group = "Help"
app.meta["--version"].group = "Help"


#
# CLI entry-point
#

# Set up configuration before running the actual application
@app.meta.default()
def main(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    host: Annotated[Optional[URL], Parameter(
        env_var=['PNGX_HOST'],
        group = [groups.meta_parameters, groups.meta_parameters_adhoc],
        )] = None,
    user: Annotated[Optional[str], Parameter(
        env_var = ['PNGX_USER'],
        group = [groups.meta_parameters, groups.meta_parameters_adhoc],
        validator = validators.not_empty,
        )] = None,
    password: Annotated[Optional[str], Parameter(
        env_var = ['PNGX_PASSWORD'],
        negative = "--ask-password",
        group = [groups.meta_parameters, groups.meta_parameters_adhoc, groups.password_xor_token]
        )] = None,
    ask_password: Annotated[Optional[bool], Parameter(
        show = False,
        group = [groups.meta_parameters, groups.meta_parameters_adhoc, groups.password_xor_token]
        )] = None,
    token: Annotated[Optional[str], Parameter(
        env_var = ['PNGX_TOKEN'],
        negative = "--ask-token",
        group = [groups.meta_parameters, groups.meta_parameters_adhoc, groups.password_xor_token],
        )] = None,
    ask_token: Annotated[Optional[bool], Parameter(
        show = False,
        group = [groups.meta_parameters, groups.meta_parameters_adhoc, groups.password_xor_token]
        )] = None,
    config_file: Annotated[Optional[Path], Parameter(
        name = "--config",
        env_var = ['PNGX_CONFIG'],
        group = [groups.meta_parameters, groups.meta_parameters_specific]
        )] = None,
    use_account: Annotated[Optional[account_alias], Parameter(
        name = "--use",
        group = [groups.meta_parameters, groups.meta_parameters_specific],
        validator = validators.starts_with_ascii_letters
        )] = None,
    show_config: Annotated[Optional[bool], Parameter(
        group = [groups.meta_parameters, "Help"],
        negative = [],
        show_default = False
        )] = False,
    ) -> None:

    """Initiate CLI

    Parameters
    ----------
    host: str
        The URL of your Paperless-ngx host, possibly including a custom port and/or script path.
    user: str
        Username
    password: str
        Password. Will be used to request an API token only.
    token: str
        API token.
    config_file: Path
        Path to configuration file.
    use_account: str
        Name (alias) of an account that should be used.
        
        If an account with the given alias exists, its credentials will be re-used.
        If not specified, the default account will be used (if any).
    show_config: bool
        Show path of the configuration file in use.
    """


    if ask_password:
        password = Prompt.ask("What's your password?", password=True)

    elif ask_token:
        token = Prompt.ask("What's your API token?", password=True)

    # Parse configuration
    try:
        appconfig.load(config_file, use_account)
    except ValueError as e:
        Console().print(format_cyclopts_error(e))
        sys.exit(1)

    if show_config:
        print(appconfig.filepath.absolute())
        sys.exit(0)

    # Add ad-hoc configuration
    if host and not tokens[:2] == ('auth', 'login'):
        try:
            appconfig.add_account(
                host = host,
                user = user,
                password = password,
                token = token,
                alias = "__adhoc__"
            )
        except ValueError as e:
            Console().print(format_cyclopts_error(e))
            sys.exit(1)

    elif tokens[:2] == ('auth', 'login'):
        # Pass credentials to login function
        if host:
            tokens += (host,)
        if user:
            tokens += ("--user", user)
        if password:
            tokens += ("--password", password)
        if token:
            tokens += ("--token", token)
    
    elif not appconfig.list():
        Console().print(format_cyclopts_error("No accounts configured that can be used."))
        sys.exit(1)

    # Now run the actual app
    try:
        app(tokens)
    except ValueError as e:
        Console().print(format_cyclopts_error(e))
        sys.exit(1)


def launch() -> None:
    """Run commands."""

    app.meta()
