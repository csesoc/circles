import json
import random

import requests
from server.routers.model import CONDITIONS

PATH="./algorithms/tests/exampleUsers.json"

with open(PATH, encoding="utf8") as f:
    USERS = json.load(f)

def test_error():
    x = requests.get('http://127.0.0.1:8000/courses/getCourse/COMP1234')
    assert x.status_code == 400

def test_get_a_course():
    x = requests.get('http://127.0.0.1:8000/courses/getCourse/COMP1521')

    assert x.status_code == 200
    assert x.json()['code'] == "COMP1521"
    assert not x.json()['is_multiterm']


def test_get_archived_course():
    x = requests.get('http://127.0.0.1:8000/courses/getCourse/ENGG1000')
    assert x.status_code == 200
    assert x.json()['code'] == "ENGG1000"
    assert x.json()['is_legacy'] == True


def test_get_course_all_courses():
    failed_courses = {
        course for course in CONDITIONS.keys()
        if (
            # random.random() < 0.5 and  # Comment out this line to test all courses
            requests.get(f'http://127.0.0.1:8000/courses/getCourse/{course}').status_code != 200
        )
    }

    # Offered alternate years => offered alternate years (not this year) but entry exists
    # Not Offered => it is not offered, no further information, entry exists
    known_failed_courses: set[str] = {
        'PSCY9914',  # Offered alternate years
        'BEES3223',  # Offered alternate years
        'CEIC6714',  # Not offered this year
        'PSCY9901',  # Offered alternate years
        'PSCY9912',  # Offered alternate years
        'PHCM9612',  # Not offered this year
    }
    failed_courses = failed_courses.difference(known_failed_courses)
    print(failed_courses)
    assert failed_courses == set(), f"Total of {len(failed_courses)} courses failed.\n{failed_courses}"
