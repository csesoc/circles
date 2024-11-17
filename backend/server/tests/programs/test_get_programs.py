import re

import requests


def test_sanity():
    x = requests.get('http://127.0.0.1:8000/programs/getPrograms')
    assert x.status_code == 200
    programs = x.json()['programs']
    for key, value in programs.items():
        assert re.match(r"[0-9]{4}", key)
        assert type(value) is str

def test_sanity_all():
    x = requests.get('http://127.0.0.1:8000/programs/getAllPrograms')
    assert x.status_code == 200
    programs = x.json()['programs']

    # Not actual number, just a rough lower bound
    assert len(programs) > 100

    for key, value in programs.items():
        assert re.match(r"[0-9]{4}", key)
        assert type(value) is str
