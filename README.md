# FastAPI - Cognito
FastAPI Cognito library is Python library which is built to ease usage of AWS Cognito authentication
with FastAPI framework. This library provides basic functions/tools which allows developers to 
use Cognito JWT. In the future, tools/functionalities may be extended. 
This library is inspired on [Flask-Cognito library created by JetBridge](https://github.com/jetbridge/flask_cognito).

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

* Add all required imports

```python
from fastapi_cognito import CognitoAuth, CognitoSettings, AuthHeaderPlugin
from fastapi import FastAPI

from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
```
  
All mandatory fields are defined in CognitoSettings
BaseSettings object. Settings can be provided by multiple methods. You can provide all required settings in **.yaml** or
  **.json** files, or your global BaseSettings file. Note that userpools field is Dict, **FIRST** user pool in a dict
will be set as default automatically. All fields shown in example below, are also required in .json or .yaml file
(with syntax matching those files.)

**Note: These configurations are required**

You should also import BaseSettings from pydantic if you are going to use global BaseSettings object.
* Provide settings that are mandatory for CognitoAuth library. 

```python
class Settings(BaseSettings):
    
    check_expiration = True
    jwt_header_name = "Authorization"
    jwt_header_prefix = "Bearer"
    userpools = {
      "europe": {
        "region": "COGNITO_REGION",
        "userpool_id": "COGNITO_USERPOOL_ID",
        "app_client_id": "APP_CLIENT_ID"
      }
      ...
    }
```
  
This example below shows how global BaseSettings object can be mapped to CognitoSettings object and passed as param to
CognitoAuth object. If we were using .yaml or .json, we should call **.from_yaml(_filename_)** or
**.from_json(_filename_)** methods on CognitoSettings object.

* Initialize application and settings object, also initialize CognitoAuth and pass previously created
settings as settings param.
  
```python
app = FastAPI()
settings = Settings()
cognito = CognitoAuth(settings=CognitoSettings.from_global_settings(settings))
```

* Add middleware for request context. This is required for CognitoAuth to work.

```python
app.add_middleware(
    RawContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin(),
        plugins.CorrelationIdPlugin(),
        AuthHeaderPlugin()
    )
)
```

* This example below shows a simple endpoint that is protected by Cognito, decorator is doing all the work about decoding and verifying
  Cognito JWT from request Authorization header and storing it in token param. 
  It can be used later to add more security to endpoints and to get required data about user which token belongs to.
  Endpoint will use default userpool if userpool_name param was not provided.
  
```python
@app.get("/")
@cognito.cognito_auth_required()
def hello_world():
  # This method will get token from request context
  token = cognito.get_token()
  # This method will retrieve Cognito ID from token stored in request context
  cognito_id = cognito.get_cognito_id()
    return {"message": "Hello world"}
```
You can also change userpool that should be used when calling cognito_auth_required() method by passing
**userpool_name** param. If **userpool_name** param is not provided, default userpool will be used.

```python
@app.get("/")
@cognito.cognito_auth_required(userpool_name="europe")
def hello_world():
    return {"message": "Hello world"}
```

There are some additional methods such as check_cognito_groups(token, groups) which will check if cognito:groups value
from **_token_** param matches the value passed in **_groups_** param, and it will restrict or allow access to users.
This method is not fully tested, and it may produce some problems.