import json
import requests
from server.tests.user.utility import clear, get_token, get_token_headers

PATH = "server/example_input/example_local_storage_data.json"

with open(PATH, encoding="utf8") as f:
    DATA = json.load(f)


def test_validateTermPlanner_empty_planner():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["empty_year"], headers=headers)

    x = requests.get(
        'http://127.0.0.1:8000/planner/validateTermPlanner', headers=headers)
    assert x.status_code == 200
    assert x.json()['courses_state'] == {}


def test_validateTermPlanner_valid_progress():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["simple_year"], headers=headers)
    x = requests.get(
        'http://127.0.0.1:8000/planner/validateTermPlanner', headers=headers)
    assert x.status_code == 200
    assert x.json()['courses_state'] == {
        "COMP1511": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "MATH1141": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "MATH1081": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "COMP1521": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "COMP1531": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "COMP2521": {
            "is_accurate": True,
            "handbook_note": "",
            "unlocked": True,
            "warnings": []
        },
        "ENGG2600": {
            'handbook_note': 'Please refer to the course overview section for further information on requirements',
            'is_accurate': True,
            'unlocked': False,
            'warnings': ['((42 UOC required in all courses you have 38 UOC))']
        }
    }


def test_validateTermPlanner_invalid_progress():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["no_uoc"], headers=headers)

    x = requests.get(
        'http://127.0.0.1:8000/planner/validateTermPlanner', headers=headers)
    assert x.status_code == 200
    assert x.json()['courses_state'] == {
        "COMP1511": {
            "is_accurate": True,
            "unlocked": True,
            "handbook_note": "",
            "warnings": []
        },
        "MATH1141": {
            "is_accurate": True,
            "unlocked": True,
            "handbook_note": "",
            "warnings": []
        },
        "MATH1081": {
            "is_accurate": True,
            "unlocked": True,
            "handbook_note": "",
            "warnings": []
        },
        "COMP1521": {
            "is_accurate": True,
            "unlocked": True,
            "handbook_note": "",
            "warnings": []
        },
        "COMP2511": {
            "is_accurate": True,
            "unlocked": False,
            "handbook_note": "",
            "warnings": ['((COMP1531 AND (COMP2521 OR COMP1927)))']
        },
        "COMP4128": {
            "is_accurate": True,
            "unlocked": False,
            "handbook_note": "",
            "warnings": [
                '((COMP3821 OR (COMP3121 AND Requires 75 WAM in all courses.  Your WAM in all courses has not been recorded)))'
            ]
        }
    }


def test_validateTermPlanner_out_of_order_progress():
    # if the courses here were shuffled, it would be correct. Show error still
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json=DATA["out_of_order"], headers=headers)
    x = requests.get(
        'http://127.0.0.1:8000/planner/validateTermPlanner', headers=headers)
    assert x.status_code == 200
    assert x.json()['courses_state'] == {
        "MATH1241": {
            "is_accurate": True,
            "unlocked": False,
            "handbook_note": "",
            "warnings": ['((Need 65 in MATH1131 for this course OR Need 65 in MATH1141 for this course OR Need 65 in DPST1013 for this course))']
        },
        "MATH1141": {
            "is_accurate": True,
            "unlocked": True,
            "handbook_note": "",
            "warnings": []
        }
    }
