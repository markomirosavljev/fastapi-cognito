class CognitoAuthError(Exception):
    """
    Default exception that will be raised each time an error is in relation with
    CognitoAuth
    """
    def __init__(self, error, description, status_code=401, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers

    def __repr__(self) -> str:
        return f"Cognito Auth Error: {self.error}"

    def __str__(self) -> str:
        return f"{self.error} - {self.description}"
