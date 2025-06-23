from typing import Union, List, Set, Optional, Tuple

from pydantic import BaseModel, HttpUrl, Field


class UserpoolModel(BaseModel):
    region: str
    userpool_id: str
    app_client_id: Optional[Union[str, List[str], Set[str], Tuple[str]]] = None
    jwks_url: Optional[str] = Field(default=None)


class CognitoToken(BaseModel):
    origin_jti: Optional[str] = None
    cognito_id: str = Field(alias="sub")
    event_id: Optional[str] = None
    token_use: str
    scope: str
    auth_time: int
    iss: HttpUrl
    exp: int
    iat: int
    jti: str
    client_id: str
    username: str
