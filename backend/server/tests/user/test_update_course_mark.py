import json

import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

def test_updateCourseMark():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    requests.put(
        'http://127.0.0.1:8000/user/updateCourseMark', json={
            'course': 'COMP1511',
            'mark': 75
        }, headers=headers)
    user = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert user['courses']['COMP1511']['mark'] == 75
