"""Paperless API client"""

from typing import Self

import httpx
from pypaperless import PaperlessClient
from pypaperless.const import DEFAULT_TIMEOUT

from pypaperless_cli.config import config as appconfig

class PaperlessAsyncAPI(PaperlessClient):
    """Represent the Paperless API"""

    def __init__(self):
        self._http_client = httpx.AsyncClient(
            headers={"User-Agent": f"pypaperless-cli/0.1-dev (https://github.com/marcelbrueckner/paperless-ngx-cli)"},
            timeout=DEFAULT_TIMEOUT,
        )
        super().__init__(appconfig.current.host, appconfig.current.token, client=self._http_client)

        # Don't care about warnings
        self.logger.setLevel("ERROR")

    async def __aenter__(self) -> Self:
        try:
            return await super().__aenter__()
        except BaseException:
            await self._http_client.aclose()
            raise

    async def __aexit__(self, *args: object) -> None:
        """Close the session, including the caller-owned httpx client (never closed by pypaperless)."""
        try:
            await super().__aexit__(*args)
        finally:
            await self._http_client.aclose()
