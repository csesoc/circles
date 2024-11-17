import json
import requests

from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)

def test_no_courses_completed():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_no_courses"], headers=headers)

    x = requests.post(
        'http://127.0.0.1:8000/courses/coursesUnlockedWhenTaken/COMP1511', json={}, headers=headers)
    assert x.json() == {
        "direct_unlock": [
            'COMP1521',
            'COMP1531',
            'COMP2041',
            'COMP2121',
            'COMP2521',
            'COMP9334',
            'MMAN9350',
        ],
        # COMP1511 is equivalent to 'DPST1091' so it unlocks DPST1093
        # Maybe "equivalent" courses should be under `direct_unlock`?
        "indirect_unlock": ["DPST1093"]
    }


def test_malformed_request():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_no_courses"], headers=headers)

    x = requests.post(
        'http://127.0.0.1:8000/courses/coursesUnlockedWhenTaken/&&&&&', {}, headers=headers)
    assert x.status_code == 400
    x = requests.post(
        'http://127.0.0.1:8000/courses/coursesUnlockedWhenTaken/COMPXXXX', {}, headers=headers)
    assert x.status_code == 400


def test_two_courses_completed():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["sample_user_1"], headers=headers)

    requests.put(
        'http://127.0.0.1:8000/user/updateCourseMark',
        json={
            'course': 'COMP1511',
            'mark': 84
        },
        headers=headers
    )

    requests.put(
        'http://127.0.0.1:8000/user/updateCourseMark',
        json={
            'course': 'COMP1521',
            'mark': 57
        },
        headers=headers
    )

    x = requests.post(
        'http://127.0.0.1:8000/courses/coursesUnlockedWhenTaken/COMP2521', {}, headers=headers)
    # TABL2710 is unlocked because USER1 now meets the 18UOC requirement
    assert x.json() == {
        "direct_unlock": [
            "COMP3121",
            "COMP3141",
            "COMP3151",
            "COMP3161",
            "COMP3231",
            "COMP3311",
            "COMP3331",
            "COMP3411",
            "COMP3431",
            "COMP3821",
            "COMP3891",
            "COMP6451",
            "COMP6714",
            "COMP6991",
            "COMP9319",
            "COMP9417",
            "COMP9444",
            "COMP9517",
            "COMP9727",
            "MTRN2500",
        ],
        "indirect_unlock": ["BABS3301", "BEIL0011", "COMP4920", "MUSC2117", "TABL2710"]
    }
