import requests
import timeit


users_data = []
for i in range(1, 1001):
    user_data = {
        "username": f"load_test_{i}",
        "email": f"load_test_{i}@email.com",
        "password": "1234",
        "password_confirmation": "1234",
        "profile": {}
    }
    users_data.append(user_data)

start = timeit.default_timer()

for user_data in users_data:
    response = requests.post(url='http://127.0.0.1:8000/user-auth/register/', json=user_data)
    print(response.json())


stop = timeit.default_timer()

print('Register Time of 1000 users: ', stop - start)