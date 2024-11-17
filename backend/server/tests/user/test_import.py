import json

import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)


def test_import_empty():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    x = requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["empty_year"], headers=headers)
    assert x.status_code == 200


def test_import_simple():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    x = requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    assert x.status_code == 200

    data = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers)
    assert data.status_code == 200
    data = data.json()
    assert "COMP6447" in data['planner']['unplanned']
