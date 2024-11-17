import json

import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

def test_toggleSummerTerm():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    x = requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["summer_term"], headers=headers)
    assert x.status_code == 200
    data = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers)
    assert data.json()["planner"]["isSummerEnabled"]
    requests.post('http://127.0.0.1:8000/user/toggleSummerTerm', headers=headers)
    data = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers)
    assert not data.json()["planner"]["isSummerEnabled"]
    assert data.json()["planner"]["years"][0]["T0"] == []
    assert data.json()["planner"]["years"][1]["T0"] == []
    assert data.json()["planner"]["unplanned"] == [
        "COMP1511", "MATH1141", "MATH1081"]
