from typing import Optional
import boto3

__client = boto3.client(
        "cognito-idp",
        endpoint_url="http://fastapi-cognito-cognito-1:9229/",
        region_name="us-east-1",
        aws_access_key_id = "local",
        aws_secret_access_key = "local"
    )

def generate_access_token(client_id: str, username: str, password: str) -> Optional[str]:
    try:
        response = __client.initiate_auth(

            ClientId = client_id,
            AuthFlow = "USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )
        return response["AuthenticationResult"]["AccessToken"]
    except boto3.ClientError as e:
        print(f"Error authenticating user: {e}")
        return None