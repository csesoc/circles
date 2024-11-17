import json

import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

def test_updateCourseMark_back_time_2019():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    user_before = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    requests.put(
        f'http://127.0.0.1:8000/user/updateStartYear', headers=headers, json={"startYear": 2019})
    user_after = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert len(user_before['planner']['years']) == len(user_after['planner']['years'])
    assert user_before['planner']['years'] == user_after['planner']['years']
    assert user_after['planner']['startYear'] == 2019
    

def test_updateCourseMark_back_time_2018():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    user_before = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    requests.put(
        f'http://127.0.0.1:8000/user/updateStartYear', headers=headers, json={"startYear": 2018})
    user_after = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert len(user_before['planner']['years']) == len(user_after['planner']['years'])
    assert user_before['planner']['years'] == user_after['planner']['years']
    assert user_after['planner']['startYear'] == 2018

def test_updateCourseMark_forward_time_2021():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put(
        'http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    user_before = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    requests.put(
        f'http://127.0.0.1:8000/user/updateStartYear', headers=headers, json={"startYear": 2021})
    user_after = requests.get(f'http://127.0.0.1:8000/user/data/all', headers=headers).json()
    assert len(user_before['planner']['years']) == len(user_after['planner']['years'])
    assert user_before['planner']['years'] == user_after['planner']['years']
    assert user_after['planner']['startYear'] == 2021
