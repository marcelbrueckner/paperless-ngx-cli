"""Store authentication information"""

from typing import Optional

from tomlkit import table

class Account():
    """Store a single account and its credentials."""

    def __init__(
        self,
        host: str,
        user: Optional[str] = None,
        token: Optional[str] = None,
        alias: Optional[str] = None
        ) -> None:
        """Instantiate account"""

        # TODO: store host and protocol in separate fields to allow nicer __str__ 
        self.host = host
        self.user = user
        self.token = token
        self.alias = alias


    def to_toml(self) -> table:
        """Serializes account information into a TOML table"""

        toml = table()

        toml.add("host", self.host)
        if self.user:
            toml.add("user", self.user)
        if self.token:
            toml.add("token", self.token)
        if self.alias:
            toml.add("alias", self.alias)
        
        return toml


    def __str__(self):
        """Serialize account information."""

        if self.user:
            s = f"{self.__class__}: {self.user}@{self.host} ({self.alias})"
        else:
            s = f"{self.__class__}: {self.host} ({self.alias})"

        return s
