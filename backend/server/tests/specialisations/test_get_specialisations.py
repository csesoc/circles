import re

import requests
from hypothesis import given
from hypothesis.strategies import sampled_from

programs = [
    *requests.get("http://127.0.0.1:8000/programs/getPrograms")
    .json()["programs"]
    .keys()
]

@given(sampled_from(programs))
def test_sanity(program):
    # this can break if 3778 disappears
    last_digit_mapper = {
        'majors': "1",
        'minors': "2",
        'honours': "H"
    }
    for typespec in ['majors', 'minors', 'honours']:
        x = requests.get(f'http://127.0.0.1:8000/specialisations/getSpecialisations/{program}/{typespec}')
        if x.status_code == 404:
            continue
        assert x.status_code == 200
        majors = x.json()['spec']
        for subprogram in majors.values():
            assert subprogram['is_optional'] is not None
            assert subprogram['notes'] is not None
            del subprogram['notes']
            del subprogram['is_optional']
            for majors in subprogram.values():
                for key, value in majors.items():
                    assert re.match(r"[A-Z]{5}" + last_digit_mapper[typespec], key)
                    assert type(value) is str

def test_nonexistant():
    x = requests.get('http://127.0.0.1:8000/specialisations/getSpecialisations/2434/honours')
    assert x.status_code == 400
