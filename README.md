# FastAPI - Cognito
FastAPI library that ease usage of AWS Cognito Auth.
This library provides basic functionalities for decoding, validation and parsing
Cognito JWT tokens and for now it does not support sign up and sign in features.

Library supports both HTTP and WebSocket connection auth.

## Requirements

* Python >=3.8
* FastAPI 
* AWS Cognito Service

## How to install
### Pip Command
```
pip install fastapi-cognito
```
## How to use
This is the simple example of how to use this package:
* Create app

```python
from fastapi import FastAPI

app = FastAPI()
```
  
All mandatory fields are added in CognitoSettings
BaseSettings object. Settings can be added in different ways.
You can provide all required settings in **.yaml** or **.json** files,
or your global BaseSettings object. Note that `userpools` field is Dict and
**FIRST** user pool in a dict will be set as default automatically if
`userpool_name` is not provided in CognitoAuth object.
All fields shown in example below, are also required in .json or .yaml file
(with syntax matching those files.)

* Provide settings that are mandatory for CognitoAuth to work. You can provide
one or more userpools.
  * `app_client_id` field for userpool besides string, can contain multiple string values provided within 
    list, tuple or set

```python
from pydantic_settings import BaseSettings
from pydantic.types import Any

class Settings(BaseSettings):
    check_expiration: bool = True
    jwt_header_prefix: str = "Bearer"
    jwt_header_name: str = "Authorization"
    userpools: dict[str, dict[str, Any]] = {
        "eu": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": ["APP_CLIENT_ID_1", "APP_CLIENT_ID_2"] # Example with multiple ids
        },
        "us": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": "APP_CLIENT_ID"
        },
        ...
    }

settings = Settings()
```
  
This example below shows how global BaseSettings object can be mapped to
CognitoSettings and passed as param to CognitoAuth.
If we were using .yaml or .json, we should call **.from_yaml(_path_)** or
**.from_json(_path_)** methods on CognitoSettings object.

* Instantiate CognitoAuth and pass previously created settings as settings param.
  
```python
from fastapi_cognito import CognitoAuth, CognitoSettings

# default userpool(eu) will be used if there is no userpool_name param provided.
cognito_eu = CognitoAuth(
  settings=CognitoSettings.from_global_settings(settings)
)
cognito_us = CognitoAuth(
  settings=CognitoSettings.from_global_settings(settings), userpool_name="us"
)
```

* This is a simple endpoint that requires authentication, it uses FastAPI 
dependency injection to resolve all required operations and get Cognito JWT.
  
```python
from fastapi_cognito import CognitoToken
from fastapi import Depends

@app.get("/")
def hello_world(auth: CognitoToken = Depends(cognito_eu.auth_required)):
    return {"message": "Hello world"}
```

### Optional authentication

If authentication should be optional, we can use ```cognito_eu.auth_optional```

Example:
```python
from fastapi_cognito import CognitoToken
from fastapi import Depends

@app.get("/")
def hello_world(auth: CognitoToken = Depends(cognito_eu.auth_optional)):
    return {"message": "Hello world"}
```

### Custom Token Model
This feature adds possiblity to use any token type for authentication(e.g. parsing ID token).

In case your token payload contains additional values, you can provide custom
token model instead of `CognitoToken`. If there is no custom token model
provided, `CognitoToken` will be set as a default model. Custom model should
be provided to `CognitoAuth` object, and should be set as type of `auth` 
variable for endpoint dependency.

Example:
```python
class CustomTokenModel(CognitoToken):
    custom_value: Optional[str] = None


cognito = CognitoAuth(
    settings=CognitoSettings.from_global_settings(settings),
    # Here we provide custom token model
    custom_model=CustomTokenModel
)

@app.get("/")
# Type of `auth` should be custom token Class
def hello_world(auth: CustomTokenModel = Depends(cognito.auth_required)):
    return {"message": f"Hello {auth.custom_value}"}
```

#### Custom Cognito attributes
Custom attributes in Cognito starts with `custom:`, which is the issue for 
parsing this variable with pydantic because of the colon. To parse custom 
attributes, add the full name of Cognito attribute to Pydantic Field alias.

```python
class CustomTokenModel(CognitoToken):
    custom_value: Optional[str] = Field(alias="custom:custom_attr")
```
Pydantic will automatically parse value by alias if specified. Make sure that
you have default value set if attribute is optional.

### OpenAPI docs authentication 
To use tokens to authenticate requests using OpenAPI docs, you can
create wrapper class. 
```python
from fastapi.security import HTTPBearer
from starlette.requests import Request
from fastapi_cognito import CognitoToken

class CognitoAuth(HTTPBearer):
    async def __call__(self, request: Request) -> CognitoToken:
        return await cognito.auth_required(request=request)

cognito_auth = CognitoAuth()

@router.get("/")
async def test_endpoint(auth: CognitoToken = Depends(cognito_auth)):
    return JSONResponse(
        status_code=200, content={"detail": "Success"}
    )
```
This will show button for adding authentication token to the request.

### Using custom JWKS URL for userpool
If you need to use custom JWKS URL for userpool, for example when you're running
cognito-local for local development, you can specify JWKS_URL configuration per
userpool. 
```python
class Settings(BaseSettings):
    userpools: dict[str, dict[str, Any]] = {
        "eu": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": "APP_CLIENT_ID",
            "jwks_url": "https://local-cognito-idp:port/jwks.json"
        }
        ...
    }
```
By setting this configuration, CognitoAuth will automatically use this url to
retrieve JWKS for userpool. If configuration is not set, CognitoAuth will 
generate URL in the following format 
`https://cognito-idp.<region>.amazonaws.com/<userpool_id>/.well-known/jwks.json`
and will use that URL to retrieve JWKS.

There is global configuration through environment variable 
`AWS_COGNITO_KEYS_URL` which is supported for backward 
compatibility with previous dependency on `cognitojwt` library. 
CognitoAuth will prioritise in the following order:
* `jwks_url` configuration per userpool,
* `AWS_COGNITO_KEYS_URL` environment variable if set,
* default value of `https://cognito-idp.<region>.amazonaws.com/<userpool_id>/.well-known/jwks.json`