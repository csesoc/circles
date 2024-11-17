import json
import requests

from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

MARKS = {
    "COMP9242": 81,
    "COMP3231": 61,
    "COMP2521": 57,
    "COMP1531": 66,
    "COMP1521": 57,
    "COMP1511": 84
}

def test_no_dependencies():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_2"], headers=headers)

    for code, mark in MARKS.items():
        requests.put('http://127.0.0.1:8000/user/updateCourseMark',
            json={
                'course': code,
                'mark': mark
            },
            headers=headers
        )

    x = requests.post("http://127.0.0.1:8000/courses/unselectCourse/COMP1531", json={}, headers=headers)
    assert x.status_code == 200
    assert x.json()["courses"] == ["COMP1531", "COMP9242"]

def test_multiple_dependencies():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_2"], headers=headers)

    for code, mark in MARKS.items():
        requests.put('http://127.0.0.1:8000/user/updateCourseMark',
            json={
                'course': code,
                'mark': mark
            },
            headers=headers
        )

    x = requests.post("http://127.0.0.1:8000/courses/unselectCourse/COMP1511", json={}, headers=headers)
    assert x.status_code == 200
    assert x.json()["courses"] == ["COMP1511", "COMP1521", "COMP1531", "COMP2521", "COMP3231", "COMP9242"]

def test_invalid_course():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_2"], headers=headers)

    for code, mark in MARKS.items():
        requests.put('http://127.0.0.1:8000/user/updateCourseMark',
            json={
                'course': code,
                'mark': mark
            },
            headers=headers
        )

    x = requests.post('http://127.0.0.1:8000/courses/unselectCourse/BADC0000', json={}, headers=headers)
    assert x.status_code == 200
