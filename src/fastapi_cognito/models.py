from typing import Union, List, Set, Optional, Tuple

from pydantic import BaseModel, HttpUrl, Field


class UserpoolModel(BaseModel):
    region: str
    userpool_id: str
    app_client_id: Union[str, List[str], Set[str], Tuple[str]]


class CognitoToken(BaseModel):
    origin_jti: str
    cognito_id: str = Field(alias="sub")
    event_id: Optional[str]
    token_use: str
    scope: str
    auth_time: int
    iss: HttpUrl
    exp: int
    iat: int
    jti: str
    client_id: str
    username: str
