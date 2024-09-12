"""
Handle application configuration.
"""

from pathlib import Path
from typing import List, Optional

import httpx
from xdg_base_dirs import xdg_config_home
from tomlkit import (
    dumps,
    parse,
    document,
    comment,
    nl,
    table
)

from pypaperless_cli.config.account import Account


class CLIConfig:
    """Parse or persist configuration"""

    __accounts: List[Account] = []
    __current_account: Account = None

    def __init__(self) -> None:
        """Instantiate a CLI configuration."""
        pass

    def load(
            self,
            filepath: Optional[Path] = None,
            use_account: Optional[str] = None
        ) -> None:
        """Load existing configuration from file."""

        if filepath is not None:
            self.filepath = filepath

            if filepath.is_file():
                self.__parse_config(filepath.read_text())
        
        else:
            config_search_paths = [
                Path.cwd().joinpath("pngx.toml"),
                xdg_config_home().joinpath("pngx", "pngx.toml")
            ]

            for filepath in config_search_paths:
                self.filepath = filepath

                if filepath.is_file():
                    self.__parse_config(filepath.read_text())
                    break

        if use_account:
            self.use_account(use_account)


    @property
    def current(self) -> Account:
        """Return the default account"""

        return self.__current_account


    def list(self) -> List[Account]:
        """Return account list"""

        return self.__accounts


    def get_account(self, alias: str) -> None:
        """Return the account with the given alias"""

        for account in [x for x in self.__accounts if x.alias == alias]:
            return account

        raise ValueError(f"Given alias ({alias}) does not match existing accounts.")



    def use_account(self, alias: str) -> None:
        """Set the default account"""

        self.__current_account = self.get_account(alias)


    def add_account(
        self,
        host: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        alias: str = "default"
    ):
        """Add or update an account"""

        # TODO: remove any trailing slash and/or /api/* script path
        # TODO: check if pypaperless supports unauthenticated requests or remote user auth
        #       (otherwise it doesn't make sense to support it when adding account)

        # If no credentials have been provided, the API might be accessible without authentication
        # (e.g. because a reverse proxy is adding required authentication header to the request)
        if all([p == None for p in [user, password, token]]):
            response = httpx.get(f"{host}/api/profile/")
            if response.status_code != 200:
                raise ValueError(f"Server {host} requires authentication.")
        
        # If neither password nor API token has been specified,
        # try Remote User authentication header
        # TODO: Make actual header name configurable?
        elif user != None and all([p == None for p in [password, token]]):
            response = httpx.get(f"{host}/api/profile/", headers = {'Remote-User': user})
            if response.status_code != 200:
                raise ValueError(f"Server {host} requires authentication for user {user}.")
        
        # Otherwise, request API token
        elif password != None:
            response = httpx.post(f"{host}/api/token/", data = {'username': user, 'password': password})
            if response.status_code != 200:
                raise ValueError(f"Invalid credentials for {user}@{host}.")
            token = response.json()['token']
        
        else:
            response = httpx.get(f"{host}/api/profile/", headers = {'Authorization': f'Token {token}'})
            if response.status_code != 200:
                raise ValueError(f"Invalid token.")

        # At this point, credentials have been verified
        for i, account in enumerate(self.__accounts):
            if account.alias == alias:
                account.host = host
                if user:
                    account.user = user
                if token:
                    account.token = token

                self.__accounts[i] = account
                self.__current_account = account
                break

        else:
            account = Account(
                host = host,
                user = user,
                token = token,
                alias = alias
            )

            self.__accounts.append(account)
            self.__current_account = account

        self.write()


    def remove_account(
        self,
        alias: str
    ) -> None:
        """Remove a named account from the configuration"""

        account = self.get_account(alias)

        self.__accounts.remove(account)
        
        if self.__accounts and self.__current_account.alias == alias:
            self.__current_account = self.__accounts[0]
        elif not self.__accounts:
            self.__current_account = None

        self.write()


    def rename_account(
        self,
        alias: str,
        new_alias: str
    ) -> None:
        """Rename an existing account"""

        if alias == new_alias:
            return
        
        for i, account in enumerate(self.__accounts):
            if account.alias == alias:
                account.alias = new_alias
                self.__accounts[i] = account

                if self.__current_account.alias == alias:
                    self.__current_account = account

                break

        self.write()


    def __parse_config(self, content: str) -> None:
        """Parse configuration information.
        
        Parameters
        ----------
        config : str
            The configuration that should be parsed.
        """
        
        config = parse(content)

        try:
            config.item('accounts')
        except:
            raise ValueError(f"Invalid configuration file.")

        current_account_alias = config.item('accounts').get('current')

        if not current_account_alias:
            return

        for k, _ in [(k, _) for k, _ in config.item('accounts').items() if k != "current"]:
            item = config.item('accounts').get(k)

            account = Account(
                host = item.get('host'),
                user = item.get('user'),
                token = item.get('token'),
                alias = item.get('alias'),
            )

            if account.alias == current_account_alias:
                self.__current_account = account

            self.__accounts.append(account)


    def serialize(self) -> str:
        """Serialize configuration"""

        content = document()

        content.add(comment("Paperless-ngx CLI configuration"))
        content.add(comment("https://github.com/marcelbrueckner/paperless-ngx-cli"))
        content.add(nl())

        accounts = table()

        if self.__current_account:
            accounts.add("current", self.__current_account.alias)
        else:
            accounts.add(comment("No accounts configured. Add them via `pngx auth login`."))
            
        for account in self.__accounts:
            accounts.add(account.alias, account.to_toml())

        content.add("accounts", accounts)

        return dumps(content)


    def write(self) -> None:
        """Write configuration to disk"""

        # Ad-hoc credentials should not be persisted
        if self.__current_account and self.__current_account.alias == '__adhoc__':
            return
        
        if not self.filepath.is_file():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)

        self.filepath.write_text(self.serialize())


config = CLIConfig()
