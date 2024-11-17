import json

import requests

from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)


def test_fix_wam_only_unlock_given_course():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_2"], headers=headers)

    x = requests.post(
        "http://127.0.0.1:8000/courses/getAllUnlocked", json={}, headers=headers
    )
    assert x.status_code != 500
    assert x.json()["courses_state"]["COMP1521"]["unlocked"] is True
    assert x.json()["courses_state"]["COMP1521"]["is_accurate"] is True


def test_unlock_dependent_course():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_one_math"], headers=headers)

    requests.put(
        'http://127.0.0.1:8000/user/updateCourseMark',
        json={
            'course': 'MATH1131',
            'mark': 100
        },
        headers=headers
    )

    x = requests.post(
        "http://127.0.0.1:8000/courses/getAllUnlocked", json={}, headers=headers
    )
    assert x.status_code != 500
    print(x.json())
    assert x.json()["courses_state"]["MATH1231"]["unlocked"] is True
    assert x.json()["courses_state"]["MATH1231"]["is_accurate"] is True
