from requests import Request
from requests.auth import AuthBase

class BearerTokenAuth(AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, request: Request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request