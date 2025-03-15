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
            "region": "eu-central-1",
            "userpool_id": "local_75ELcB6t",
            "app_client_id": "75eys17xtiq3hyfo9co7d1zti",
            "jwks_url": "http://fastapi-cognito-cognito-1:9229/local_75ELcB6t/.well-known/jwks.json"
        },
        "us": {
            "region": "us-east-1",
            "userpool_id": "local_4Wg2XYXC",
            "app_client_id": "5021s8dh9hnskm0zgrwl0pvco",
            "jwks_url": "http://fastapi-cognito-cognito-1:9229/local_4Wg2XYXC/.well-known/jwks.json"
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


@app.get("/eu")
def hello_world(auth: CognitoToken = Depends(cognito_eu.auth_required)):
    return {"message": "Hello world"}

@app.get("/us")
def hello_world(auth: CognitoToken = Depends(cognito_us.auth_required)):
    return {"message": "Hello world"}

@app.get("/optional")
def hello_world(auth: CognitoToken = Depends(cognito_eu.auth_optional)):
    return {"message": "Hello world"}