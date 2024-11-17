"""
Tests for the `termsOffered/{course}/{year}` routes.

Tests for data can be run against specific examples from legacy year 2021.
Be careful with anything from the LIVE_YEAR as that may change.
Anything further back is not guaranteed either.

TODO: Figure out why terms don't work for old data - pre-2021 or so.
    - Exist on handbook
    - Don't exist in our data.
"""

import requests
from data.config import LIVE_YEAR


def test_term_offered_comp1511_2021():
    res = requests.get("http://127.0.0.1:8000/courses/termsOffered/COMP1511/2021")

    assert res.status_code == 200
    data = res.json()

    assert data.get("fails", []) == []
    assert set(data.get("terms", {}).get("2021", [])) == { "T1", "T2", "T3" }

def test_term_offered_comp1511_bad_years_past():
    res = requests.get(f"http://127.0.0.1:8000/courses/termsOffered/COMP1511/2001")

    assert res.status_code == 200
    data = res.json()

    fails = data.get("fails", [])
    assert check_year_in_fails("2001", fails)

def test_term_offered_comp1511_future_year():
    res_current = requests.get(f"http://127.0.0.1:8000/courses/termsOffered/COMP1511/{LIVE_YEAR}")
    assert res_current.status_code == 200
    data_current = res_current.json().get("terms", {}).get(str(LIVE_YEAR), [])

    res_future = requests.get(f"http://127.0.0.1:8000/courses/termsOffered/COMP1511/{LIVE_YEAR + 1}")
    assert res_future.status_code == 200
    data_current = res_future.json().get("terms", {}).get(str(LIVE_YEAR + 1), [])

    assert data_current == data_current

def test_term_offered_fake_course():
    res = requests.get("http://127.0.0.1:8000/courses/termsOffered/CODEXXXX/2020+2021+2022")

    assert res.status_code == 200
    data = res.json()

    fails = data.get("fails", [])
    assert len(fails) == 3
    assert check_year_in_fails("2020", fails)
    assert check_year_in_fails("2021", fails)
    assert check_year_in_fails("2022", fails)

def check_year_in_fails(year, fails):
    return any(
        year in fail for fail in fails
    )

