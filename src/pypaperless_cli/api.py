"""Paperless API client"""

from aiohttp import ClientSession
from pypaperless import Paperless

from pypaperless_cli.config import config as appconfig

class PaperlessAsyncAPI(Paperless):
    """Represent the Paperless API"""

    def __init__(self):
        session = ClientSession(headers={"User-Agent": f"pypaperless-cli/0.1-dev (https://github.com/marcelbrueckner/paperless-ngx-cli)"})
        super().__init__(appconfig.current.host, appconfig.current.token, session=session)

        # Don't care about warnings
        self.logger.setLevel("ERROR")
