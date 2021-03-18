#FastAPI - Cognito
FastAPI Cognito library is Python library which is built to ease usage of AWS Cognito authentication
with FastAPI framework. This library was built for personal usage on single project, and it has only
essential and necessary functions/tools that we needed on our project, in future it may be extended
with more tools.This package will be deployed on our AWS CodeArtifact.

##Requirements

Before we start using this library, there are some requirements:
* Python >=3.8
* FastAPI 
* AWS Cognito Service
* AWS CLI

##How to install
* Configure a client with login command:
```
aws codeartifact login --tool pip --domain {domain} --domain-owner {domain_owner} --repository {repository}
```
This command will set pip to use index-url of repository passed in --repository option.

First step is to install this package into your local environment by executing the following command in 
terminal:

**Note: This will install from a repository configured with** _aws codeartifact login_ 
```
pip install fastapi-cognito
```
If we want to install packages from pypi, execute the following command:
```
pip install -i https://pypi.org/simple {library}
```

##How to use
This is the simple example of how to use this package:

* Add all required imports
```
from fastapi_cognito import CognitoAuth
from fastapi import FastAPI, Depends
from pydantic import BaseSettings
```
* Create Settings class that inherits BaseSettings from pydantic:

**Note: These configurations are required**
```
class Settings(BaseSettings):
    COGNITO_REGION = 'YOUR_AWS_REGION'
    COGNITO_USERPOOL_ID = 'COGNITO_USERPOOL_ID'
    COGNITO_APP_CLIENT_ID = 'COGNITO_APP_CLIENT_ID'
    COGNITO_CHECK_TOKEN_EXPIRATION = True
    COGNITO_JWT_HEADER_NAME = 'Authorization'
    COGNITO_JWT_HEADER_PREFIX = 'Bearer'
```
* Initialize application and settings object, also initialize CognitoAuth and pass previously created
settings as settings param.
```

app = FastAPI()
settings = Settings()
cognito = CognitoAuth(settings=settings)
```
* This is a simple endpoint that is protected by cognito, when dependency is resolved, cognito_token will
store decoded and verified Cognito JWT token. It can be used later to add more security to endpoints and
  to get required data about user which token belongs to.
```
@app.get('/')
def hello_world(cognito_token=Depends(cognito.cognito_auth_required)):
    return {'message': 'Hello world'}
```
There are some additional methods such as check_cognito_groups(token, groups) which will check if cognito:groups value
from **_token_** param matches the value passed in **_groups_** param, and it will restrict or allow access to users.