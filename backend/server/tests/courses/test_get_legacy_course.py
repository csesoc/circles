"""
Tests the `courses/getLegacyCourse` route to ensure that legacy
data is working.
"""

import json
from typing import Annotated, Any, Optional

import requests

with open(
    "./server/tests/courses/test_objects.json", "r", encoding="utf-8"
) as f:
    TEST_OBJECTS = json.load(f)["legacy_courses"]


def get_legacy_course_wrapper(year: int, course: str):
    """
    Wrapper for `/courses/getLegacyCourse/{year}/{courseCode}` endpoint
    """
    return requests.get(
        f"http://127.0.0.1:8000/courses/getLegacyCourse/{year}/{course}"
    )

def compare_course_details(
        output, expected, compare_desc: bool=False
    ) -> dict[str, Any]:
    """
    Used to compare two course-detail objects.
    Returns the key (str) that had a differing value, otherwise None.
    By default, this skips the description value. Add the `compare_desc` flag
    to toggle this behaviour.
    """
    assert set(dict(output).keys()) == set(dict(expected).keys())
    if compare_desc:
        if output["description"] != expected["description"]:
            return {
                "key": Annotated[str, "description"],
                "given": Annotated[str, output["description"]],
                "expected": Annotated[str, expected["description"]]
            }

    del output["description"]
    del expected["description"]
    diff = {
        key: { "given": output[key], "expected": expected[key] }
        for key, expected_val in expected.items()
        if output[key] != expected_val
    }
    return diff


def test_legacy_comp1511():
    """
    Test for COMP1511
    """
    res_2019 = get_legacy_course_wrapper(2019, "COMP1511")
    assert res_2019.status_code == 200
    assert not compare_course_details(res_2019.json(), TEST_OBJECTS["comp1511_2019"])

    res_2020 = get_legacy_course_wrapper(2020, "COMP1511")
    assert res_2020.status_code == 200
    assert not compare_course_details(res_2020.json(), TEST_OBJECTS["comp1511_2020"])

    res_2021 = get_legacy_course_wrapper(2021, "COMP1511")
    assert res_2020.status_code == 200
    assert not compare_course_details(res_2021.json(), TEST_OBJECTS["comp1511_2021"])

def def_test_legacy_course_error():
    """
    Test for a course that doesn't exist or, in a year that the course doesn't
    exist in.
    """
    assert get_legacy_course_wrapper(2019, "COMP9999").status_code == 400
    assert get_legacy_course_wrapper(2020, "COMP9999").status_code == 400
    assert get_legacy_course_wrapper(2021, "COMP9999").status_code == 400
    assert get_legacy_course_wrapper(2022, "COMP9999").status_code == 400

    assert get_legacy_course_wrapper(2050, "COMP1511").status_code == 400
    assert get_legacy_course_wrapper(2049, "COMP1511").status_code == 400
    assert get_legacy_course_wrapper(2018, "COMP1511").status_code == 400
    assert get_legacy_course_wrapper(2017, "COMP1511").status_code == 400

def test_legacy_comp6991():
    """
    Test for legacy COMP6991.
    This is example of a course that is new and only available in recent years.
    """
    assert get_legacy_course_wrapper(2019, "COMP6991").status_code == 400
    assert get_legacy_course_wrapper(2020, "COMP6991").status_code == 400
    assert get_legacy_course_wrapper(2021, "COMP6991").status_code == 400

def test_legacy_math3361():
    """
    Test for legacy math3361.
    Useful because this is a course that run but then stopped running.
    Running every second year:tm: (lol math why u lie and hurt me like this)
    However, it still has legacy handbook entries in the years that it doesn't run.
    """
    res2019 = get_legacy_course_wrapper(2019, "MATH3361")
    assert res2019.status_code == 200
    assert not compare_course_details(res2019.json(), TEST_OBJECTS["math3361_2019"])

    res2020 = get_legacy_course_wrapper(2020, "MATH3361")
    assert res2020.status_code == 200
    assert not compare_course_details(res2020.json(), TEST_OBJECTS["math3361_2020"])

    res2021 = get_legacy_course_wrapper(2021, "MATH3361")
    assert res2021.status_code == 200
    assert not compare_course_details(res2021.json(), TEST_OBJECTS["math3361_2021"])

    res2022 = get_legacy_course_wrapper(2022, "MATH3361")
    assert res2022.status_code == 200
    assert not compare_course_details(res2022.json(), TEST_OBJECTS["math3361_2022"])
