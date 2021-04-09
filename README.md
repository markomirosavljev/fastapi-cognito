# FastAPI - Cognito
FastAPI Cognito library is Python library which is built to ease usage of AWS Cognito authentication
with FastAPI framework. This library was built for personal usage on a single project, and it has only
essential and necessary functions/tools that we needed on our project, in future it may be extended
with more tools.This package will be deployed in our GitLab Repository and when library is completely functional
and tested, it will be published on PyPi for public usage.

## Requirements

Before we start using this library, there are some requirements:
* Python >=3.8
* FastAPI 
* AWS Cognito Service

## How to install

### Pip Command
```
pip install fastapi-cognito --extra-index-url https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/25240961/packages/pypi/simple
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
  **.json** files, or your global BaseSettings file. Note that userpools field is Dict, **first** user pool in a dict
will be set as default automatically. All fields shown in example below, are also required in .json or .yaml file
(with syntax matching those files.)

**Note: These configurations are required**

You should also import BaseSettings from pydantic if you are goind to use global BaseSettings object.
* Provide settings that are mandatory for CognitoAuth library. 

```python
class Settings(BaseSettings):
    
    check_expiration = True
    jwt_header_name = 'Authorization'
    jwt_header_prefix = 'Bearer'
    userpools = {
      "europe": {
        "region": "eu-west-1",
        "userpool_id": "COGNITO_USERPOOL_ID",
        "app_client_id": "APP_CLIENT_ID"
      }
      ...
    }
```
  
This example is showing how global BaseSettings object can be mapped to CognitoSettings object and passed as param to
CognitoAuth object. If we were using .yaml or .json, we should call **.from_yaml(_filename_)** or
**.from_json(_filename_)** methods on CognitoSettings object. If we used any other method, we don't need **settings**
variable.

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

* This is a simple endpoint that is protected by cognito, decorator is doing all the work about decoding and verifying
  Cognito JWT from request Authorization header and storing it in token param. 
  It can be used later to add more security to endpoints and to get required data about user which token belongs to.
  Method will use default userpool if userpool_name param was not provided.
  
```python
@app.get('/')
@cognito.cognito_auth_required()
def hello_world():
  # This method will get token from request context
  token = cognito.get_token()
  # This method will retrieve Cognito ID from token stored in request context
  cognito_id = cognito.get_cognito_id()
    return {'message': 'Hello world'}
```
You can also change userpool that should be used when calling cognito_auth_required() method by passing
**userpool_name** param, in other case, method will use default userpool.

```python
@app.get('/')
@cognito.cognito_auth_required(userpool_name="europe")
def hello_world():
    return {'message': 'Hello world'}
```

There are some additional methods such as check_cognito_groups(token, groups) which will check if cognito:groups value
from **_token_** param matches the value passed in **_groups_** param, and it will restrict or allow access to users.