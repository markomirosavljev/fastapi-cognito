from typing import Any

from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings

from fastapi_cognito import CognitoAuth, CognitoSettings, CognitoToken

app = FastAPI()


class Settings(BaseSettings):
    check_expiration: bool = True
    jwt_header_prefix: str = "Bearer"
    jwt_header_name: str = "Authorization"
    userpools: dict[str, dict[str, Any]] = {
        "eu": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": "APP_CLIENT_ID"
        },
        "us": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": "APP_CLIENT_ID"
        }
    }


settings = Settings()

cognito_eu = CognitoAuth(
    settings=CognitoSettings.from_global_settings(settings)
)
cognito_us = CognitoAuth(
    settings=CognitoSettings.from_global_settings(settings),
    userpool_name="us"
)


@app.get("/")
def hello_world(auth: CognitoToken = Depends(cognito_us.auth_required)):
    return {"message": "Hello world"}
