"""
Supporting classes for Requirements which have some condition attached
to a specific category
"""

import json
import re
from abc import ABC, abstractmethod

from algorithms.objects.helper import Logic

# Preload the mappings to school and faculty
CACHED_MAPPINGS = {}

with open("./algorithms/cache/courseMappings.json", "r", encoding="utf8") as f:
    CACHED_MAPPINGS = json.load(f)


class Category(ABC):
    """
    The base Category class from which more detailed Category classes
    stem from
    """

    @abstractmethod
    def match_definition(self, course: str) -> bool:
        """ a definition of how a course fits in a category """
        pass

    @abstractmethod
    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return self.__str__()


class CompositeCategory(Category):
    """ Composed of other categories, evaluated with either Any or All """

    def __init__(self, logic: Logic = Logic.AND):
        self.categories: list[Category] = []
        self.logic = logic

    def add_category(self, category: Category):
        """ Adds a category object """
        self.categories.append(category)

    def set_logic(self, logic: Logic):
        """ AND or OR """
        self.logic = logic

    def match_definition(self, course: str) -> bool:
        if self.logic == Logic.AND:
            return all(
                category.match_definition(course) for category in self.categories
            )
        if self.logic == Logic.OR:
            return any(
                category.match_definition(course) for category in self.categories
            )
        raise ValueError(f"Invalid logic: {self.logic}")


    def __str__(self) -> str:
        logic_op = "&&" if self.logic == Logic.AND else "||"
        return f"({f' {logic_op} '.join(str(category) for category in self.categories)})"


class AnyCategory(Category):
    """ Wildcard category `*` that matches to anything """

    def match_definition(self, course: str) -> bool:
        return True

    def __str__(self) -> str:
        return "all courses"


class ClassCategory(Category):
    """ Category that matches to a specific class """

    def __init__(self, class_name: str):
        self.class_name = class_name

    def match_definition(self, course: str) -> bool:
        return self.class_name == course

    def __str__(self) -> str:
        return self.class_name


class CourseCategory(Category):
    """ A 4 letter course category, e.g. COMP, SENG, MATH, ENGG """

    def __init__(self, code: str):
        self.code = code

    def match_definition(self, course: str) -> bool:
        return bool(re.match(rf"^{self.code}\d{{4}}$", course))

    def __str__(self) -> str:
        return f"{self.code} courses"


class LevelCategory(Category):
    """ A simple level category. e.g. L2 """

    def __init__(self, level: int):
        # A number representing the level
        self.level = level

    def match_definition(self, course: str) -> bool:
        return bool(course[4] == str(self.level))

    def __str__(self) -> str:
        return f"level {self.level} courses"


class LevelCourseCategory(CompositeCategory):
    """ A level category for a certain type of course (e.g. L2 MATH) """

    def __init__(self, level: int, code: str):
        super().__init__()
        self.add_category(LevelCategory(level))
        self.add_category(CourseCategory(code))


class SchoolCategory(Category):
    """Category for courses belonging to a school (e.g. S Mechanical)"""

    def __init__(self, school):
        self.school = school  # The code for the school (S Mechanical)

    def match_definition(self, course: str) -> bool:
        return course in CACHED_MAPPINGS[self.school]

    def __str__(self) -> str:
        return self.school


class FacultyCategory(Category):
    """ Category for courses belonging to a faculty (e.g. F Business) """

    def __init__(self, faculty: str):
        self.faculty = faculty  # The code for the faculty (F Business)

    def match_definition(self, course: str) -> bool:
        return course in CACHED_MAPPINGS[self.faculty]

    def __str__(self) -> str:
        return self.faculty


class GenEdCategory(Category):
    """
    Category for a course being a Gened
        - This is condition is unique in the sense that it's matching is
          contingent on the user's program

    NOT IMPLEMENTED!!!!!!
    """

    def __init__(self):
        pass

    def match_definition(self, course: str) -> bool:
        # TODO: Implement this
        return False

    def __str__(self) -> str:
        return "GenEdCategory"
