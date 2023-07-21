from typing import Dict, Any

from cognitojwt import CognitoJWTException, decode_async as cognito_jwt_decode
from fastapi.exceptions import HTTPException
from jose import JWTError
from pydantic_settings import BaseSettings
from requests.exceptions import ConnectionError as HttpConnectionError
from starlette.requests import Request

from .exceptions import CognitoAuthError
from .models import UserpoolModel, CognitoToken


class CognitoAuth(object):
    """
    Base class which handles config and provides required methods.
    """

    def __init__(
            self,
            settings: BaseSettings,
            userpool_name: str = None,
            custom_model=None
    ):
        """
        Initialization
        :param settings: BaseSettings object with configurations
        :param userpool_name: Optional param which determines which userpool
         configuration to apply.
        :param custom_model: Custom Pydantic model that should be used to parse
         token claims
        """
        self._userpool_name: str = userpool_name
        self._userpool: UserpoolModel
        self._jwt_header_name: str
        self._jwt_header_prefix: str
        self._check_expiration: bool
        if custom_model:
            self._cognito_token_model = custom_model
        else:
            self._cognito_token_model = CognitoToken

        self._add_settings(settings)

    def _add_settings(self, settings) -> None:
        """
        Set all required configurations from settings object and check validity
        for each config with `_get_required_settings` method
        :param settings: BaseSettings object where configurations should be
         provided.
        :return: None
        """
        self._userpool = self._get_required_setting(
            settings=settings,
            config="userpools",
            config_key=self._userpool_name
        )
        self._jwt_header_name = self._get_required_setting(
            settings=settings,
            config="jwt_header_name"
        )
        self._jwt_header_prefix = self._get_required_setting(
            settings=settings,
            config="jwt_header_prefix"
        )
        self._check_expiration = self._get_required_setting(
            settings=settings,
            config="check_expiration"
        )

    @staticmethod
    def _get_required_setting(
            settings,
            config,
            config_key: str = None
    ) -> [str, Dict]:
        """
        This method checks if required setting is provided in `settings`
        object. If value for setting exists in provided `settings` object this
        method will return that value. If this method is used to configure
        userpool, it will read `config_key` param if provided and set userpool
        to userpool with name that matches `config_key` value, else it will use
        first provided userpool
        :param settings: BaseSettings object from which app should read all
         configurations
        :param config: single configuration that should be set
        :param config_key: if config is dict, this key will be used to access
         required value.
        :return: value of configuration
        """
        try:
            if config_key and config == "userpools":
                val = UserpoolModel(
                    **settings.__getattribute__(config)[config_key]
                )
            elif config_key:
                val = settings.__getattribute__(config)[config_key]
            elif not config_key and config == "userpools":
                key = list(settings.__getattribute__(config).keys())[0]
                val = UserpoolModel(**settings.__getattribute__(config)[key])
            else:
                val = settings.__getattribute__(config)
        except KeyError:
            raise CognitoAuthError(
                "Configuration error",
                f"`{config_key}` userpool not found in "
                f"`{config}` from Settings object."
            )
        except AttributeError as error:
            raise CognitoAuthError(
                "Configuration error",
                f"{config} not found in settings object but it is required.") \
                from error
        return val

    @staticmethod
    def _get_optional_setting(settings, config, default_value) -> any:
        """
        Set optional setting if provided
        :param settings: BaseSettings object from which app should read
         configurations
        :param config: name of configuration in provided `settings` object
        :param default_value: Value to set if setting is not provided in
         `settings` object
        :return: value to set or None
        """
        try:
            val = settings.__getattribute__(config)
            return val if val else default_value
        except AttributeError:
            return default_value

    def _verify_header(self, auth_header_value: str) -> str:
        """
        Check if value in `Authorization` header is valid and return that value
        :param auth_header_value: `Authorization` header value sent with
         request.
        :return: Authorization header value(token)
        """
        if not auth_header_value:
            raise HTTPException(
                status_code=401,
                detail="Request does not contain well-formed Cognito JWT"
            )

        header_parts = auth_header_value.split()
        if self._jwt_header_prefix not in header_parts:
            raise HTTPException(
                status_code=401,
                detail="Invalid Cognito JWT Header - "
                       f"Missing authorization header prefix "
                       f"`{self._jwt_header_prefix}`"
            )

        if header_parts[0].lower() != self._jwt_header_prefix.lower():
            raise HTTPException(
                status_code=401,
                detail=f"Invalid Cognito JWT Header - "
                       f"Unsupported authorization type. "
                       f"Header prefix '{header_parts[0].lower()}' does not "
                       f"match '{self._jwt_header_prefix.lower()}'"
            )
        elif len(header_parts) == 1:
            raise HTTPException(
                status_code=401,
                detail="Invalid Cognito JWT Header - Token missing"
            )
        elif len(header_parts) > 2:
            raise HTTPException(
                status_code=401,
                detail="Invalid Cognito JWT Header - Token contains spaces"
            )

        return header_parts[1]

    async def _decode_token(self, token) -> Dict:
        """
        This method will use cognito_jwt_decode to decode token and verify if
        token is valid
        :param token: token retrieved from `Authorization` header.
        :return: decoded and verified cognito token or 401.
        """
        try:
            return await cognito_jwt_decode(
                token=token,
                region=self._userpool.region,
                userpool_id=self._userpool.userpool_id,
                app_client_id=self._userpool.app_client_id,
                testmode=not self._check_expiration
            )
        except TypeError:
            raise HTTPException(
                status_code=401,
                detail="Unable to get userpool key,"
                       " your userpool_id config might be incorrect."
            )
        except (ValueError, JWTError):
            raise HTTPException(
                status_code=401,
                detail="Malformed authentication token"
            )
        except HttpConnectionError:
            raise HTTPException(
                status_code=500,
                detail="Unable to establish connection with AWS, "
                       "your userpool region config might be incorrect."
            )

    async def auth_optional(self, request: Request) -> Any:
        """
        Optional authentication, method will try to parse `Authorization` header
        if present, else it will return None
        :param request: Incoming request
        :return: Token Model or None
        """
        authorization_header = request.headers.get(
            self._jwt_header_name.lower()
        )

        if not authorization_header:
            return None

        token = self._verify_header(auth_header_value=authorization_header)

        try:
            payload = await self._decode_token(token=token)
        except CognitoJWTException as error:
            raise HTTPException(status_code=401, detail=str(error))
        return self._cognito_token_model(**payload)

    async def auth_required(self, request: Request) -> Any:
        """
        Get token from request `Authorization` header use `_verify_header` to
        verify value, extract token payload with `_decode_token` and return
        TokenModel with token payload data.
        :return: TokenModel with token payload or 401.
        """
        token = self._verify_header(
            request.headers.get(self._jwt_header_name.lower())
        )

        try:
            payload = await self._decode_token(token=token)
        except CognitoJWTException as error:
            raise HTTPException(status_code=401, detail=str(error))
        return self._cognito_token_model(**payload)
