import base64
import binascii
import json
import time
from typing import Union, Container, Dict, Mapping

from fastapi_cognito.cognito_jwt.exceptions import CognitoJWTException

CLIENT_ID_KEYS: Dict[str, str] = {
    'access': 'client_id',
    'id': 'aud'
}


def check_expired(exp: int, testmode: bool = False) -> None:
    """
    Check if JWT token is expired if test mode is not enabled.
    """
    if time.time() > exp and not testmode:
        raise CognitoJWTException("Token is expired.")


def check_client_id(
        claims: Dict,
        app_client_id: Union[str, Container[str]]
) -> None:
    """
    Check if JWT is issued for audience with provided `app_client_id`
    """
    token_use = claims["token_use"]

    client_id_key: str = CLIENT_ID_KEYS.get(token_use)

    if not client_id_key:
        raise CognitoJWTException(
            f"Invalid token use {token_use}."
            f" Valid values: {list(CLIENT_ID_KEYS.keys())}"
        )

    if isinstance(app_client_id, str):
        app_client_id = (app_client_id,)

    if claims[client_id_key] not in app_client_id:
        raise CognitoJWTException(
            "Token was not issued for this client id audience."
        )


def base64url_decode(value: str) -> bytes:
    """
    Decodes token header and claims and fix padding if not correct
    """
    rem = len(value) % 4

    if rem > 0:
        value += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(value)


def __get_token_header(jwt: str) -> Dict[str, str]:
    """
    Retrieve JWT token header without validation

    :return: Unvalidated JWT token header
    """
    if isinstance(jwt, str):
        jwt = jwt.encode("utf-8")
    try:
        signing_input, crypto_segment = jwt.rsplit(b".", 1)
        header_segment, claims_segment = signing_input.split(b".", 1)
        header_data = base64url_decode(header_segment)
    except ValueError:
        raise CognitoJWTException("Not enough segments.")
    except (TypeError, binascii.Error):
        raise CognitoJWTException(f"Invalid header padding.")

    try:
        header = json.loads(header_data.decode("utf-8"))
    except ValueError as e:
        raise CognitoJWTException("Invalid header string: {}".format(e))

    return header


def get_unverified_token_header(jwt: str) -> Mapping[str, str]:
    return __get_token_header(jwt)
