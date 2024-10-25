import json

import requests

from server.tests.user.utility import clear, get_token, get_token_headers

with open("./algorithms/tests/exampleUsers.json", encoding="utf8") as f:
    USER = json.load(f)["user_degree_wizard"]
f.close()


def test_search_course():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.post('http://127.0.0.1:8000/user/setupDegreeWizard', headers=headers, json=USER)
    x = requests.post('http://127.0.0.1:8000/courses/searchCourse/COMP1', headers=headers)
    assert x.status_code == 200
    assert x.json().get("COMP1521") is not None


def test_search_archives():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.post('http://127.0.0.1:8000/user/setupDegreeWizard', headers=headers, json=USER)
    x = requests.post('http://127.0.0.1:8000/courses/searchCourse/DESN1000', headers=headers)
    assert x.status_code == 200
    assert x.json().get("DESN1000") is not None


def test_search_title():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.post('http://127.0.0.1:8000/user/setupDegreeWizard', headers=headers, json=USER)
    x = requests.post('http://127.0.0.1:8000/courses/searchCourse/Programming Fundamentals', headers=headers)
    assert x.json().get("COMP1511") is not None


def test_search_minor():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.post('http://127.0.0.1:8000/user/setupDegreeWizard', headers=headers, json=USER)
    x = requests.post('http://127.0.0.1:8000/courses/searchCourse/Financial Fundamentals', headers=headers)
    assert x.status_code == 200
    assert x.json().get("ACCT2511") is not None
