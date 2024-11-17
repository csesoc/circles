""" test file for categories """
import json

from algorithms.objects.categories import CourseCategory, LevelCategory, LevelCourseCategory

# need to test if the UOC and WAM mathods are correct for 1 case only

# rest need tests for their match_definition

PATH = "./algorithms/tests/exampleUsers.json"

with open(PATH, encoding="utf8") as f:
    USERS = json.load(f)


def test_course_category_match_definition():
    courseCategory = CourseCategory("PAIN")
    assert not courseCategory.match_definition("PAIN")
    assert courseCategory.match_definition("PAIN1234")
    assert not courseCategory.match_definition("PAIN123")
    assert not courseCategory.match_definition("PAIN12345")


def test_level_category_match_definition():
    level1 = LevelCategory(1)
    assert level1.match_definition("COMP1000")
    assert level1.match_definition("ENGG1100")
    assert not level1.match_definition("ENGG3100")


def test_level_course_category_match_definition():
    level1comp = LevelCourseCategory(1, "COMP")
    assert level1comp.match_definition("COMP1000")
    assert not level1comp.match_definition("COMP3000")
    assert not level1comp.match_definition("ENGG1100")
    assert not level1comp.match_definition("ENGG3100")
