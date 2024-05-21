import json


def save_users(users):
    with open('/data/users.json', 'w') as f:
        json.dump(users, f)
