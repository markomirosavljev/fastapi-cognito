from typing import Union, List, Set, Optional, Tuple

from pydantic import BaseModel, HttpUrl, Field, UUID4


class UserpoolModel(BaseModel):
    region: str
    userpool_id: str
    app_client_id: Union[str, List[str], Set[str], Tuple[str]]


class CognitoToken(BaseModel):
    sub: UUID4 = Field(..., 
        description="A unique identifier (UUID), or subject, for the authenticated user.")
    cognito_groups: Optional[List[str]] = Field(default=None,
        alias="cognito:groups",
        description="An array of the names of user pool groups that have your user as a member.")
    iss: HttpUrl = Field(description="The issuer of the token.")
    origin_jti: Optional[str] = Field(default=None,
        description="The original ID token issued for the authentication event that triggered this webhook.")
    event_id: Optional[UUID4] = Field(default=None,
        description="The event ID of the authentication event that triggered this webhook.")
    token_use: str = Field(...,
        description="The intended purpose of the token. In an ID token, its value is id or access.")

    auth_time: int = Field(...,
        description="The time when the authentication event occurred.")
    exp: int = Field(...,
        description="The time the token expires.")
    iat: int = Field(...,
        description="The time the token was issued.")

    jti: UUID4 = Field(...,
        description="The unique identifier (UUID) of the token.")


class CognitoIdToken(CognitoToken):
    """
    Cognito ID token.
    
    Reference: <https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html>
    """
    aud: str = Field(...,
        description="The user pool app client that authenticated your user.")
    email_verified: bool = Field(...,
        description="Specifies whether the email address in the ID token is verified.")
    cognito_preferred_role: Optional[str] = Field(default=None,
        alias="cognito:preferred_role",
        description="The preferred role of the authenticated user.")
    cognito_username: str = Field(...,
        alias="cognito:username",
        description="The username of the authenticated user.")
    nonce: Optional[str] = Field(default=None,
        description="The nonce that was originally sent in the authentication request.")
    cognito_roles: Optional[List[str]] = Field(default=None,
        alias="cognito:roles",
        description="An array of the names of user pool roles that are assigned to the user.")

    identities: Optional[List[str]] = Field(default=None,
        alias="identities",
        description="Information about each third-party identity provider profile that you've linked to a user.")

    email: str = Field(...,
        description="The email address of the authenticated user.")


class CognitoAccessToken(CognitoToken):
    """
    Cognito access token.
    
    Reference: <https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html>
    """
    client_id: Field(...,
        description="The user pool app client that authenticated your user.")
    scope: str = Field(...,
        description="The OAuth scopes that are associated with the token.")
    device_key: Optional[UUID4] = Field(default=None,
        description="The unique identifier (UUID) of the authenticated user's device.")
    version: Optional[int] = Field(default=None,
        description="The version number of the token.")
    username: str = Field(...,
        description="The username of the authenticated user.")
