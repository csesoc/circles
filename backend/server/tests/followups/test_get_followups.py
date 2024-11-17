import requests


def test_error_invalid_term():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/COMP1511/&&')
    assert x.status_code == 400

def test_error_not_comp_course():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/MATH1081/T2')
    assert x.status_code == 400
    
def test_error_invalid_course():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/COMP/T2')
    assert x.status_code == 400
    
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/&&&&&&/T2')
    assert x.status_code == 400

def test_get_followups_COMP1511():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/COMP1511/T2')

    assert x.status_code == 200
    assert x.json()['originCourse'] == "COMP1511"
    assert x.json()['originTerm'] == "T2"
    assert x.json()['followups']['COMP1521'] == { "T3": 339 } 

def test_get_followups_COMP6080():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/COMP6080/T2')

    assert x.status_code == 200
    assert x.json()['originCourse'] == "COMP6080"
    assert x.json()['originTerm'] == "T2"
    assert x.json()['followups'] == {}

def test_get_followups_COMP3331():
    x = requests.get('http://127.0.0.1:8000/followups/getFollowups/COMP3331/T2')

    assert x.status_code == 200
    assert x.json()['originCourse'] == "COMP3331"
    assert x.json()['originTerm'] == "T2"
    assert x.json()['followups']['COMP4920'] == { 'T3': 63 }
    assert x.json()['followups']['COMP3900'] == { 'T3': 36 }
