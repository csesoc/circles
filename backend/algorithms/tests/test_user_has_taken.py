"""
Tests `User.has_taken_course`
    - Given a list of courses, return if the course has been taken (bool)
    - Want checks for course fail and pass
"""

import json

from algorithms.objects.user import User

EXAMPLE_USERS_PATH = "./algorithms/tests/exampleUsers.json"

with open(EXAMPLE_USERS_PATH) as f:
    USERS = json.load(f)


def test_user_has_taken_empty_user():
    """
    The user object being passed in for construction is empty.
    Note that this is differentiated from the case where the user
    has no courses.
    """
    user = User()
    assert user.has_taken_course("COMP1069") is False
    assert user.has_taken_course("COMP1511") is False
    assert user.has_taken_course("COMP1521") is False
    assert user.has_taken_course("COMP1531") is False
    assert user.has_taken_course("COMP2521") is False
    assert user.has_taken_course("COMP3521") is False


def test_user_no_courses():
    user = User(USERS["user_no_courses"])
    assert user.has_taken_course("COMP1069") is False
    assert user.has_taken_course("COMP1511") is False
    assert user.has_taken_course("COMP1521") is False
    assert user.has_taken_course("COMP1531") is False
    assert user.has_taken_course("COMP2521") is False
    assert user.has_taken_course("COMP3521") is False


def test_user_has_taken_one_course():
    user = User(USERS["user_one_course"])
    assert user.has_taken_course("COMP1511") is True
    assert user.has_taken_course("COMP1521") is False
    assert user.has_taken_course("COMP1531") is False
    assert user.has_taken_course("COMP2521") is False
    assert user.has_taken_course("COMP3521") is False


def test_user_has_taken_add_course():
    user = User()
    assert user.has_taken_course("COMP1511") is False
    user.add_courses({
        "COMP1511": (6, 100)
    })
    assert user.has_taken_course("COMP1511") is True


def test_user_has_taken_user_1():
    user = User(USERS["user1"])
    assert user.has_taken_course("COMP1511")


def test_user_has_taken_fail():
    """
    Check that the pass / fail condition works
        - especially for the 49/50 pass boundary
    """
    user_fail = User(USERS["user_fail_comp1511"])
    assert user_fail.has_taken_course("COMP1511") is False
    user_pass = User(USERS["user_bare_pass_comp1511"])
    assert user_pass.has_taken_course("COMP1511") is True


def test_user_has_taken_no_marks():
    """If no marks, want to assume that the course has been completed."""
    user = User(USERS["user1_no_marks"])
    assert user.has_taken_course("COMP1511") is True
    assert user.has_taken_course("COMP1521") is True
