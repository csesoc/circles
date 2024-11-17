"""
    Defines the `User` class which holds their data such as, courses taken,
    current course, current program, ... etc.
    The class contains methods that are used to determine whether the user
    is able to take a course.
"""

import copy
import json
import re
from itertools import chain
from typing import List, Literal, Optional, Tuple, TypedDict

from algorithms.cache.cache_config import CACHED_EQUIVALENTS_FILE, CACHED_EXCLUSIONS_FILE
from algorithms.objects.categories import AnyCategory, Category

with open(CACHED_EQUIVALENTS_FILE, "r", encoding="utf8") as f:
    CACHED_EQUIVALENTS: dict[str, dict[str, Literal[1]]] = json.load(f)

with open(CACHED_EXCLUSIONS_FILE, "r", encoding="utf8") as f:
    CACHED_EXCLUSIONS: dict[str, dict[str, Literal[1]]] = json.load(f)

class UserJSON(TypedDict, total=False):
    courses: dict[str, tuple[int, Optional[int]]]
    program: Optional[str]
    specialisations: list[str]
    year: int
    core_courses: list[str]

class User:
    """ A user and their data which will be used to determine if they can take a course """
    # pylint: disable=too-many-public-methods

    def __init__(self, data = None):
        # Will load the data if any was given
        self.courses: dict[str, Tuple[int, Optional[int]]] = {}
        self.cur_courses: dict[str, Tuple[int, Optional[int]]] = {}
        self.program: Optional[str] = None
        self.specialisations: list[str] = []
        self.year: int = 0
        self.core_courses: list[str] = []

        # Data was provided
        if data is not None:
            self.load_json(data)

    def add_courses(self, courses: dict[str, Tuple[int, Optional[int]]]):
        """
        Given a dictionary of courses mapping course code to a (uoc, grade) tuple,
        adds the course to the user and updates the uoc/grade at the same time.
        this will update the data if the course has been taken already
        """
        self.courses.update(courses)

    def add_current_course(self, course_code: str, course: Tuple[int, Optional[int]]):
        """
        Given a course the user is taking in their current term,
        adds it to their cur_courses
        """
        self.cur_courses[course_code] = course

    def add_current_courses(self, courses: dict[str, Tuple[int, Optional[int]]]):
        """
        Takes in a list of courses (represented as strings by course
        code) and, adds it to the list of current courses.
        """
        self.cur_courses = self.cur_courses | courses

    def empty_current_courses(self):
        """
        Empty all the current courses. Helps with moving
        on to the next term in the term planner api
        """
        self.cur_courses = {}

    def add_program(self, program: str):
        """ Adds a program to this user """
        self.program = program

    def add_specialisation(self, specialisation: str):
        """ Adds a specialisation to this user """
        self.specialisations.append(specialisation)

    def has_taken_specific_course(self, course):
        """ taken a course directly, no equivalents """
        return course in self.courses

    def has_taken_course(self, course: str):
        """ Determines if the user has taken this course """
        return any(
            c in self.courses and (self.courses[c][1] or 50) >= 50
            for c in chain([course], (CACHED_EQUIVALENTS.get(course) or []))
        )

    def is_taking_specific_course(self, course):
        """ taking a course directly, no equivalents """
        return course in self.cur_courses

    def is_taking_course(self, course: str):
        """ Determines if the user is taking this course this term """
        return course in self.cur_courses or any(c in self.cur_courses for c in (CACHED_EQUIVALENTS.get(course) or []))

    def in_program(self, program: str):
        """ Determines if the user is in this program code """
        return self.program == program

    def get_courses(self):
        """ get all course codes """
        return list(self.courses.keys())

    def get_courses_with_uoc(self) -> List[Tuple[str, int]]:
        return [
            (course, uoc)
            for course, (uoc, _) in self.courses.items()
        ]

    def in_specialisation(self, specialisation: str):
        """ Determines if the user is in the specialisation """
        # Escape specialisations and replace '?'s with wildcards
        wildcarded = re.escape(specialisation).replace(r'\?', r'[A-Z0-9]')
        pat = f"^{wildcarded}$"

        # Search for it in the users' specialisations
        return any(
            bool(re.match(pat, spec, flags=re.IGNORECASE))
            for spec in self.specialisations
        )

    def load_json(self, data: UserJSON):
        """ Given the user data, correctly loads it into this user class """

        if "program" in data:
            self.program = copy.deepcopy(data["program"])
        if "specialisations" in data:
            self.specialisations = copy.deepcopy(data["specialisations"])
        if "courses" in data:
            self.courses = copy.deepcopy(data["courses"])
        if "year" in data:
            self.year = copy.deepcopy(data["year"])
        if "core_courses" in data:
            self.core_courses = copy.deepcopy(data["core_courses"])

    def get_grade(self, course: str):
        """
        Given a course which the student has taken, returns their
        grade (or None for no grade)
        """
        return self.courses.get(course, (6, None))[1]

    def wam(self, category: Category = AnyCategory()) -> Tuple[Optional[float], bool]:
        """
        Calculates the user's WAM by taking the average of the sum of their
        marks, weighted by uoc per course.
        Will return `None` is the user has taken no uoc, and a boolean indicating if all uoc have an associated mark.
        """
        total_mark, total_uoc, counted_uoc = 0, 0, 0
        for course, (uoc, grade) in self.courses.items():
            if category.match_definition(course):
                total_uoc += uoc
                if grade is not None:
                    counted_uoc += uoc
                    total_mark += uoc * grade

        return (None if counted_uoc == 0 else total_mark / counted_uoc, total_uoc == counted_uoc and counted_uoc != 0)

    def uoc(self, category: Category = AnyCategory()):
        """ Given a user, returns the number of units they have taken for this uoc category """
        return sum(
            uoc
            for course, (uoc, _) in self.courses.items()
            if category.match_definition(course)
        )

    def completed_core(self, category: Category = AnyCategory()):
        """ Checks that the user has completed all core courses matching a category """
        return self.matches_core(list(self.courses.keys()), category)[0]

    def matches_core(self, courses: list[str], category: Category = AnyCategory()):
        """ Checks that the user has listed all core courses matching a category """
        has_done = {
            course: False for course in self.core_courses
            if category.match_definition(course)
        }
        relevant_courses = []
        old_courses = dict(self.courses)
        self.add_courses({course: (6, None) for course in courses if course not in self.courses.keys()})
        for course in has_done:
            if self.has_taken_course(course):
                if has_done.get(course, True) is False or not all(has_done.get(exclusion, True) for exclusion in CACHED_EXCLUSIONS.get(course, {}).keys()):
                    # this course flipped something
                    relevant_courses.append(course)
                has_done[course] = True
                for exclusion in CACHED_EXCLUSIONS.get(course, {}).keys():
                    if exclusion in has_done:
                        has_done[exclusion] = True
        # reset courses
        self.courses = old_courses
        return all(has_done.values()), relevant_courses

    def pop_course(self, course: str) -> Tuple[int, Optional[int]]:
        """
            Removes a course from done courses and returns its uoc and mark
        """
        return self.courses.pop(course)
