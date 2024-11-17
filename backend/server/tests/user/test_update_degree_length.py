import json

import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

def test_updateDegreeLength_extend():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    requests.put(
        f'http://127.0.0.1:8000/user/updateDegreeLength', headers=headers, json={"numYears": 4})
    user_after = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert len(user_after['planner']['years']) == 4
    assert user_after['planner']['years'][0] == { "T0": [], "T1": [ "COMP1511", "MATH1141", "MATH1081"], "T2": [ "COMP1521", "COMP1531", "COMP2521"], "T3": []}
    assert user_after['planner']['years'][1] == {"T0": [], "T1": ["ENGG2600"], "T2": ["ENGG2600"], "T3": ["ENGG2600"]}
    assert user_after['planner']['years'][2] == {"T0": [], "T1": [], "T2": [], "T3": []}
    assert user_after['planner']['years'][3] == {"T0": [], "T1": [], "T2": [], "T3": []}

def test_updateDegreeLength_shorten():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    requests.put(
        f'http://127.0.0.1:8000/user/updateDegreeLength', headers=headers, json={"numYears": 1})
    user_after = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert len(user_after['planner']['years']) == 1
    assert user_after['planner']['years'][0] == { "T0": [], "T1": [ "COMP1511", "MATH1141", "MATH1081"], "T2": [ "COMP1521", "COMP1531", "COMP2521"], "T3": []}
    assert user_after['planner']['unplanned'] == ["COMP6447", "ENGG2600", "ENGG2600", "ENGG2600"]
