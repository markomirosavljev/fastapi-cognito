from typing import Optional, Union

from starlette.requests import HTTPConnection, Request

from starlette_context.plugins.base import Plugin


class AuthHeaderPlugin(Plugin):
    key = "Authorization"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[str]:
        """
        Extract Authorization header value to context of request
        """
        auth_header = await self.extract_value_from_header_by_key(request)
        if not auth_header:
            return None
        else:
            return auth_header
