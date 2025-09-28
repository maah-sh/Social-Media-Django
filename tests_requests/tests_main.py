import requests
from  requests_test import responses
from requests_test.custom_auth import BearerTokenAuth
from pprint import pprint

server = 'http://127.0.0.1:8000/'
username = 'testun'
password = '1234'
test_image_file = {'file': open('test_image.jpeg', 'rb')}

login_response = requests.post(url= server + 'user-auth/login/', json={"username":username, "password":password})
token = login_response.json()['token']['access']


request_kwargs_list = [
    {'method': 'GET', 'url': server + 'posts/published-posts/'},
    {'method': 'GET', 'url': server + 'posts/user-posts/', 'auth': BearerTokenAuth(token)},
    {'method': 'POST', 'url': server + 'posts/post/', 'auth': BearerTokenAuth(token),
     'files': test_image_file , 'data':{"content":"content of test post by requests"}},
    {'method': 'GET', 'url': server + 'posts/post/7/', 'auth': BearerTokenAuth(token)},
    {'method': 'PUT', 'url': server + 'posts/post/5/', 'auth': BearerTokenAuth(token), 'json': {"published": "True"}},
    {'method': 'DELETE', 'url': server + 'posts/post/16/', 'auth': BearerTokenAuth(token)},
]

for kwargs in request_kwargs_list:
    response = requests.request(**kwargs)
    pprint(responses.response_info(response))

