import json
import logging
import os
from typing import Dict, Container, Optional, Union, List, Mapping

import httpx
from aiofile import AIOFile
from async_lru import alru_cache
from joserfc import jwk, jwt
from joserfc.errors import BadSignatureError

from fastapi_cognito.cognito_jwt.constants import PUBLIC_KEYS_URL_TEMPLATE
from fastapi_cognito.cognito_jwt.exceptions import CognitoJWTException
from fastapi_cognito.cognito_jwt.utils import check_expired, check_client_id, \
    get_unverified_token_header

logger = logging.getLogger(__name__)


@alru_cache(maxsize=10)
async def __get_keys_async(keys_url: str) -> List[dict]:
    """
    Retrieves public keys from AWS Cognito or read from file

    :return: List of public keys
    """
    try:
        if keys_url.startswith("http"):
            async with httpx.AsyncClient() as client:
                response = await client.get(keys_url)
                data = response.json()
        else:
            async with AIOFile(keys_url, 'r') as afp:
                f = await afp.read()
                data = json.loads(f)
        return data.get('keys')
    except Exception as e:
        logger.error(
            f"ERROR: Following error occurred while retrieving jwks from "
            f"`{keys_url}`: {e} - "
            f"Check if your configuration `settings.jwks_url` or "
            f"`AWS_COGNITO_KEYS_URL` environment variable is correct."
        )
        raise CognitoJWTException("Failed to decode JWT token.")


async def __get_public_key_async(
        token: str,
        region: str,
        userpool_id: str,
        jwks_url: Optional[str] = None
):
    """
    Get public key, verify that `kid` value matches value from token headers
    and generate `joserfc._keys.Key` object

    :return: `joserfc._keys.Key`
    """
    if not jwks_url:
        jwks_url: str = (
            os.environ.get("AWS_COGNITO_KEYS_URL") or
            PUBLIC_KEYS_URL_TEMPLATE.format(region, userpool_id)
        )
    keys: list = await __get_keys_async(jwks_url)

    headers: Mapping[str, str] = get_unverified_token_header(token)
    kid: str = headers["kid"]

    key = list(filter(lambda k: k["kid"] == kid, keys))
    if not key:
        raise CognitoJWTException(
            "Public key not found, check userpool configuration."
        )
    else:
        key = key[0]

    return jwk.JWKRegistry.import_key(key)


async def decode_cognito_jwt(
        token: str,
        region: str,
        userpool_id: str,
        app_client_id: Optional[Union[str, Container[str]]] = None,
        testmode: bool = False,
        jwks_url: Optional[str] = None,
) -> Dict:
    """
    Retrieve public key, decode and validate JWT. Check if token is issued
     for provided `app_client_id` and if it's expired.

    :return: Dict with token claims.
    """
    public_key = await __get_public_key_async(
        token=token, region=region, userpool_id=userpool_id, jwks_url=jwks_url
    )

    try:
        decoded_claims = jwt.decode(token, public_key)
    except BadSignatureError:
        raise CognitoJWTException(
            "Token signature verification failed."
        )

    claims = decoded_claims.claims
    check_expired(claims["exp"], testmode=testmode)

    if app_client_id:
        check_client_id(claims, app_client_id)

    return claims
