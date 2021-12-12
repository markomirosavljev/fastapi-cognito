# FastAPI - Cognito
FastAPI extension that is build to ease usage of  AWS Cognito Auth with FastAPI.
This library provides basic functions/tools which allow developers to use
Cognito JWT.

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
or your global BaseSettings file. Note that userpools field is Dict,
**FIRST** user pool in a dict will be set as default automatically if
userpool_name is not provided in CognitoAuth object initialization.
All fields shown in example below, are also required in .json or .yaml file
(with syntax matching those files.)

You should also import BaseSettings from pydantic if you are going to use global BaseSettings object.
* Provide settings that are mandatory for CognitoAuth library. You can provide
one or more userpools.

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    check_expiration = True
    jwt_header_prefix = "Bearer"
    jwt_header_name = "Authorization"
    userpools = {
        "eu": {
            "region": "USERPOOL_REGION",
            "userpool_id": "USERPOOL_ID",
            "app_client_id": "APP_CLIENT_ID"
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
If we were using .yaml or .json, we should call **.from_yaml(_filename_)** or
**.from_json(_filename_)** methods on CognitoSettings object.

* Initialize CognitoAuth and pass previously created settings as settings param.
  
```python
from fastapi_cognito import CognitoAuth, CognitoSettings

# default userpool(eu) will be used if there is no userpool_name param provided.
cognito_eu = CognitoAuth(settings=CognitoSettings.from_global_settings(settings))
cognito_us = CognitoAuth(settings=CognitoSettings.from_global_settings(settings), userpool_name="us")
```

* This is a simple endpoint that is protected by Cognito, it uses FastAPI 
dependency injection to resolve all required operations and get Cognito JWT.
It can be used later to add more security to endpoints and to get required
data about user which token belongs to.
  
```python
from fastapi_cognito import CognitoToken
from fastapi import Depends

@app.get("/")
def hello_world(auth: CognitoToken = Depends(cognito_eu.auth_required)):
    return {"message": "Hello world"}
```