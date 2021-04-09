from .exceptions import CognitoAuthError
from cognitojwt import CognitoJWTException, decode as cognito_jwt_decode
from jose import JWTError
from functools import wraps

from starlette_context import context
from pydantic import BaseSettings
from fastapi.exceptions import HTTPException
from typing import List, Dict

CONFIG_DEFAULTS = {
    "check_expiration": True,
    "jwt_header_name": "Authorization",
    "jwt_header_prefix": "Bearer"
}


class CognitoAuth(object):
    """
    Base class that will handle all logic about configurations, token decode and verification.
    """

    def __init__(self, settings: BaseSettings = None):
        self.userpools: dict
        self.default_userpool: str
        self.jwt_header_name: str
        self.jwt_header_prefix: str
        self.check_expiration: bool

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

        # set all required configurations from settings object and check with _get_required_setting method.
        self.userpools = self._get_required_setting(settings, "userpools")
        self.jwt_header_name = self._get_required_setting(settings, "jwt_header_name")
        self.jwt_header_prefix = self._get_required_setting(settings, "jwt_header_prefix")
        self.check_expiration = self._get_required_setting(settings, "check_expiration")

        # set all configurations based on configs read out of settings file.
        self.default_userpool = list(self.userpools.values())[0]

    @staticmethod
    def _get_required_setting(settings, config) -> [str, Dict]:
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

    def _get_token(self) -> str:
        """
        This method will get headers from request from params, and check various cases if Authorization header exists or
        if its valid.

        Method will fetch Authorization header value and split it, so it can analyse if header prefix or token string is
        valid. If everything is valid, it will return token string.
        :return: Authorization header value(token)
        """
        auth_header_value = context.get(self.jwt_header_name)
        if not auth_header_value:
            raise HTTPException(status_code=401, detail="Request does not contain well-formed Cognito JWT")

        header_parts = auth_header_value.split()
        if self.jwt_header_prefix not in header_parts:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header -"
                                                        " Missing authorization header prefix")

        if header_parts[0].lower() != self.jwt_header_prefix.lower():
            raise HTTPException(status_code=401, detail=f"Invalid Cognito JWT Header - Unsupported authorization"
                                                        f"type. Header prefix '{header_parts[0].lower()}' does not "
                                                        f"match '{self.jwt_header_prefix.lower()}'")
        elif len(header_parts) == 1:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header - Token missing")
        elif len(header_parts) > 2:
            raise HTTPException(status_code=401, detail="Invalid Cognito JWT Header - Token contains spaces")

        context.pop("Authorization")
        return header_parts[1]

    def _decode_token(self, token, userpool_name: str = None) -> Dict:
        """
        This method is using cognito_jwt_decode to decode token and verify if token is valid.
        :param token: token that needs to be decoded and verified.
        :return: decoded and verified cognito jwt claims or 401
        """
        userpool = self.userpools.get(userpool_name) if userpool_name else None
        try:
            return cognito_jwt_decode(
                token=token,
                region=userpool.get("region")if userpool else self.default_userpool.get("region"),
                userpool_id=userpool.get("userpool_id")if userpool else self.default_userpool.get("userpool_id"),
                app_client_id=userpool.get("app_client_id")if userpool else self.default_userpool.get("app_client_id"),
                testmode=not self.check_expiration
            )
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
        if "cognito:groups" not in claims or claims["cognito:groups"] is None:
            raise HTTPException(status_code=401, detail="Not Authorized - User doesn't have access to this resource")
        if all([i not in claims["cognito:groups"] for i in groups]):
            raise HTTPException(status_code=401, detail="Not Authorized - User doesn't have access to this resource")
        return True

    def _cognito_auth_required(self, userpool_name: str = None) -> Dict:
        """
        This method will get token from request context with _get_token() method, and extract decoded and verified
        payload of token with _decode_token() method. If _decode_token() method fails in any point and can't decode/
        verify token, method will raise CognitoJWTException, else, it will return decoded and verified payload.
        :return: decoded payload or 401
        """
        token = self._get_token()

        try:
            payload = self._decode_token(token=token, userpool_name=userpool_name if userpool_name else None)
        except CognitoJWTException as error:
            raise HTTPException(status_code=401, detail=str(error))
        return payload

    def cognito_auth_required(self, userpool_name: str = None):
        """
        This decorator will be used when some endpoint should be protected and will require Cognito Authentication.
        Decorator should be called as last decorator on function under all other decorators and optionally it may have
        userpool_name param that will change target userpool from default userpool set to userpool that is matching
        passed userpool_name param. When decorator resolve his tasks, it will return decoded and verified Cognito token
        into 'token' in context.
        :param userpool_name: Name of userpool that should be used for some endpoint.
        :return: updated function
        """
        def main_wrapper(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                context["token"] = self._cognito_auth_required(userpool_name=userpool_name)
                return func(*args, **kwargs)
            return wrapper
        return main_wrapper

    @staticmethod
    def get_token():
        """
        This method will return whole token payload from current request context.
        """
        return context.get("token")

    @staticmethod
    def get_cognito_id():
        """
        This method will return Cognito ID from current JWT stored in request context.
        """
        return context.get("token")["sub"]
