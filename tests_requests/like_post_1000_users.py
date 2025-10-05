import requests
import timeit

from requests_test.custom_auth import BearerTokenAuth

users_data = []
for i in range(1, 1001):
    user_data = {
        "username": f"load_test_{i}",
        "password": "1234",
    }
    users_data.append(user_data)

start = timeit.default_timer()

for user_data in users_data:
    login_response = requests.post(url='http://127.0.0.1:8000/user-auth/login/', json=user_data)
    token = login_response.json()['token']['access']

    response = requests.post(url='http://127.0.0.1:8000/posts/post/like/', auth=BearerTokenAuth(token), json={"post_id": "8"})
    print(response.json())


stop = timeit.default_timer()

print('Like Time of 1000 users: ', stop - start)