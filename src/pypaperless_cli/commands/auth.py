"""
Command to manage authentication information.
"""

import sys
from typing import Annotated, Optional

from cyclopts import App, Parameter
from cyclopts.exceptions import format_cyclopts_error

from rich.console import Console
from rich.table import Table
from rich import box

from pypaperless_cli.utils.types import (
    account_alias,
    URL
)
from pypaperless_cli.config import config as appconfig

#
# Authentication
#

auth = App(name="auth", help="Manage authentication information", version_flags=[])
auth["--help"].group = "Help"

@auth.command
def login(
    host: Annotated[URL, Parameter(env_var=['PNGX_HOST'])],
    /, *,
    user: Annotated[Optional[str], Parameter(env_var=['PNGX_USER'])] = None,
    password: Annotated[Optional[str], Parameter(env_var=['PNGX_PASSWORD'],negative="--ask-password")] = None,
    token: Annotated[Optional[str], Parameter(env_var=['PNGX_TOKEN'],negative="--ask-token")] = None,
    alias: Optional[account_alias] = "default"
    ) -> None:

    """Log in to your instance of Paperless-ngx.

    Examples
    --------
    pngx login https://paperless.example.com --user USERNAME --token TOKEN

    Parameters
    ----------
    host: str
        The URL of your Paperless-ngx host, possibly including a custom port and/or script path.
    user: str
        Username
    alias: str
        Assign the credentials provided to an account named according to the given alias.
        Allows to easily switch between multiple Paperless-ngx hosts (e.g. personal, business) on subsequent commands.

        If not specified, an implicit default account will be created.
        
        :warning: Providing an existing account alias will overwrite existing credentials.
    """

    # Add credentials
    try:
        appconfig.add_account(
            host = host,
            user = user,
            password = password,
            token = token,
            alias = alias
        )
    except ValueError as e:
        Console().print(format_cyclopts_error(e))
        sys.exit(1)


@auth.command
def logout(alias: account_alias = None, /) -> None:
    """Remove credentials from disk for the given account.

    Parameters
    ----------
    alias: account_alias
        Name of the account to be logged out from. Defaults to the account currently in use.
    """

    if alias:
        appconfig.remove_account(alias)
    else:
        appconfig.remove_account(appconfig.current.alias)


@auth.command
def use(alias: account_alias, /) -> None:
    """Set the current account

    Parameters
    ----------
    alias: account_alias
        Name of an existing account to be set as the default account.
    """
    
    appconfig.use_account(alias)
    appconfig.write()


@auth.command
def show(alias: account_alias = None, /) -> None:
    """Show details of an existing account.

    Parameters
    ----------
    alias: account_alias
        Name of an existing account. Defaults to the current account if no alias is given.
    """
    
    accounts = appconfig.list()

    if accounts:
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Alias")
        table.add_column("Host")
        table.add_column("User")
    
        if not alias:
            table.add_row(appconfig.current.alias, appconfig.current.host, appconfig.current.user)
        else:
            account = appconfig.get_account(alias)
            table.add_row(account.alias, account.host, account.user)

        Console().print(table)


@auth.command
def list() -> None:
    """List available accounts"""

    accounts = appconfig.list()

    if accounts:
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Alias")
        table.add_column("Host")
        table.add_column("User")

        for account in accounts:
            if account.alias == appconfig.current.alias:
                table.add_row(f"* {account.alias}", account.host, account.user, style="green")
            else:
                table.add_row(f"  {account.alias}", account.host, account.user)

        Console().print(table)
    
    else:
        Console().print("No accounts configured.")


@auth.command
def rename(alias: account_alias, new_alias: account_alias, /) -> None:
    """Rename an existing account.

    Parameters
    ----------
    alias: account_alias
        Name of an existing account that should be renamed.
    new_alias: account_alias
        New name of the account.
    """
    
    appconfig.rename_account(alias, new_alias)
