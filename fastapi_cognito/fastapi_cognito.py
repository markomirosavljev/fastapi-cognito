from .exceptions import CognitoAuthError
from cognitojwt import CognitoJWTException, decode as cognito_jwt_decode
from jose import JWTError

from fastapi.requests import Request
from pydantic import BaseSettings
from fastapi.exceptions import HTTPException
from typing import List

CONFIG_DEFAULTS = {
    'check_expiration': True,
    'jwt_header_name': 'Authorization',
    'jwt_header_prefix': 'Bearer'
}


class CognitoAuth(object):
    """
    Base class that will handle all logic about configurations, token decode and verification.
    """

    def __init__(self, settings: BaseSettings = None):
        self._region = None
        self._userpool_id = None
        self._jwt_header_name = None
        self._jwt_header_prefix = None
        self._check_expiration = None
        self._app_client_id = None

        if settings is not None:
            self._add_settings(settings)

    def _add_settings(self, settings):
        """
        Setting default class attributes defined in CONFIG_DEFAULTS object, and get
        :param settings: BaseSettings object from which app should read all configurations.
        :return: None
        """
        for config, value in CONFIG_DEFAULTS.items():
            self.__setattr__(config, value)

        # set all required configurations and check with _get_required_setting method.
        self._region = self._get_required_setting(settings, 'COGNITO_REGION')
        self._userpool_id = self._get_required_setting(settings, 'COGNITO_USERPOOL_ID')
        self._app_client_id = self._get_required_setting(settings, 'COGNITO_APP_CLIENT_ID')
        self._jwt_header_name = self._get_required_setting(settings, 'COGNITO_JWT_HEADER_NAME')
        self._jwt_header_prefix = self._get_required_setting(settings, 'COGNITO_JWT_HEADER_PREFIX')
        self._check_expiration = self._get_required_setting(settings, 'COGNITO_CHECK_TOKEN_EXPIRATION')

    @staticmethod
    def _get_required_setting(settings, config):
        """
        This method is used to check if required configurations exist in 'settings' object passed as param.

        Method will try to get configuration from settings object, and if it exist, the method will return value
        of that configuration and apply it to matching attribute.

        If configuration does not exist, method will  raise CognitoAuthError and warn developer what caused an error.

        :param settings: BaseSettings object from which app should read all configurations.
        :param config: single configuration that should be set
        :return: value of configuration
        """
        try:
            val = settings.__getattribute__(config)
        except AttributeError as error:
            raise CognitoAuthError(
                "Configuration error",
                f"{config} not found in settings object but it is required.") from error
        return val

    def _get_token(self, request: Request):
        """
        This method will get headers from request from params, and check various cases if Authorization header exists or
        if its valid.

        Method will fetch Authorization header value and split it, so it can analyse if header prefix or token string is
        valid. If everything is valid, it will return token string.
        :param request: Incoming request that need authorization to proceed.
        :return: Authorization header value(token)
        """
        auth_header_value = request.headers.get(self._jwt_header_name)
        if not auth_header_value:
            raise HTTPException(status_code=401, detail='Request does not contain well-formed Cognito JWT')

        header_parts = auth_header_value.split()
        if self._jwt_header_prefix not in header_parts:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header -"
                                                        " Missing authorization header prefix")

        if header_parts[0].lower() != self._jwt_header_prefix.lower():
            raise HTTPException(status_code=401, detail=f"Invalid Cognito JWT Header - Unsupported authorization"
                                                        f"type. Header prefix '{header_parts[0].lower()}' does not "
                                                        f"match '{self._jwt_header_prefix.lower()}'")
        elif len(header_parts) == 1:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header - Token missing")
        elif len(header_parts) > 2:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header - Token contains spaces")

        return header_parts[1]

    def _decode_token(self, token) -> dict:
        """
        This method is using cognito_jwt_decode to decode token and verify if token is valid.
        :param token: token that needs to be decoded and verified.
        :return: decoded and verified cognito jwt claims or 401
        """
        try:
            return cognito_jwt_decode(
                region=self._region,
                token=token,
                userpool_id=self._userpool_id,
                app_client_id=self._app_client_id)
        except (ValueError, JWTError):
            raise HTTPException(status_code=401, detail="Malformed authentication token")

    @staticmethod
    def check_cognito_groups(claims: dict, groups: List) -> [bool, None]:
        """
        This method will check if 'claims' passed as param, contain 'cognito:groups' list, and it will verify against
        'groups' param. If at least 1 element of 'cognito:groups' matches any element from 'groups' this method will
        return true, and user will have access to resource, else it will raise 401 - Unauthorized exception.
        :return: Boolean True, or 401
        """
        if 'cognito:groups' not in claims or claims['cognito:groups'] is None:
            raise HTTPException(status_code=401, detail="Not Authorized - User doesn't have access to this resource")
        if all([i not in claims['cognito:groups'] for i in groups]):
            raise HTTPException(status_code=401, detail="Not Authorized - User doesn't have access to this resource")
        return True

    def cognito_auth_required(self, request: Request) -> dict:
        """
        This method will get token from request header with _get_token() method, and extract decoded and verified
        payload of token with _decode_token() method. If _decode_token() method fails in any point and can't decode/
        verify token, method will raise CognitoJWTException, else, it will return decoded and verified payload.
        :param request: request from which this method will get authorization header with token.
        :return: decoded payload or 401
        """
        token = self._get_token(request)

        try:
            payload = self._decode_token(token)
        except CognitoJWTException as error:
            raise HTTPException(status_code=401, detail=str(error))
        return payload
