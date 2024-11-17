"""
Contains the Conditions classes
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TypedDict

from algorithms.objects.categories import AnyCategory, Category
from algorithms.objects.course import Course
from algorithms.objects.helper import Logic
from algorithms.objects.user import User
from ortools.sat.python import cp_model  # type: ignore

# CACHED
CACHED_CONDITIONS_TOKENS_PATH = "./data/final_data/conditionsTokens.json"
with open(CACHED_CONDITIONS_TOKENS_PATH, "r", encoding="utf8") as f:
    CACHED_CONDITIONS_TOKENS = json.load(f)


CACHED_PROGRAM_MAPPINGS_FILE = "./algorithms/cache/programMappings.json"
with open(CACHED_PROGRAM_MAPPINGS_FILE, "r", encoding="utf8") as f:
    CACHED_PROGRAM_MAPPINGS = json.load(f)


def get_variable(courses: list[Tuple[cp_model.IntVar, Course]], course: str) -> Optional[cp_model.IntVar]:
    var_list = [variable[0] for variable in courses if variable[0].Name() == course]
    return None if len(var_list) == 0 else var_list[0]


class CompositeJsonData(TypedDict):
    id: str
    logic: str
    children: list[dict]


class Condition(ABC):
    """
    Superclass for condition subclasses to inherit. Instances of
    `Condition` classes are representations of specific types of
    requirements / conditions from the handbook
    """
    @abstractmethod
    def validate(self, user: User) -> tuple[bool, list[str]]:
        """
        Returns a tuple first containing whether or not the course is
        unlocked, and second any warnings about the course's unlocked state
        - eg that the course needs some wam that the student has not
        entered.
        """
        pass

    @abstractmethod
    def is_path_to(self, course: str) -> bool:
        """ checks if 'course' is able to meet any subtree's requirements"""
        pass

    @abstractmethod
    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        """ add the condition directly to the model, and return all constraints generated """
        # just add straight up true or false. This default implementation works for things based only on the user, and not their courses
        is_valid, _ = self.validate(user)
        return [model.AddBoolAnd(is_valid)]

    @abstractmethod
    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        """ add the negation of the condition directly to the model, and return the constraints generated """
        # just add straight up true or false. This default implementation works for things based only on the user, and not their courses
        is_valid, _ = self.validate(user)
        return [model.AddBoolAnd(not is_valid)]

    def beneficial(self, user: User,  course: dict[str, Tuple[int, Optional[int]]]) -> bool:
        """ checks if 'course' is able to meet any *more* subtrees' requirements """
        course_name = list(course.keys())[0]
        if self.validate(user)[0] or user.has_taken_course(course_name):
            return False
        # temp check if the course is useful
        user.add_courses(course)
        answer = self.validate(user)[0]
        user.pop_course(course_name)
        return answer

    @abstractmethod
    def __str__(self) -> str:
        """ json representation """
        return super().__str__()

    def __repr__(self) -> str:
        return self.__str__()



class CourseCondition(Condition):
    """
    Condition that the student has completed this course before
    the current term
    """

    def __init__(self, course: str):
        self.course = course

    def is_path_to(self, course: str) -> bool:
        return self.course == course

    def validate(self, user: User) -> tuple[bool, list[str]]:
        return (True, []) if user.has_taken_course(self.course) else (False, [self.course])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # make sure this course happens before the given course
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var < course_variable)] if condition_var is not None else [model.AddBoolAnd(False)]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # make sure the course doesnt exist, or happens after the current course
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var >= course_variable)] if condition_var is not None else [model.AddBoolAnd(True)]

    def __str__(self) -> str:
        return json.dumps({
            'id': self.course
        })


class CoreqCourseCondition(Condition):
    """ Condition that the student has completed the course in or before the current term """
    def __init__(self, course):
        self.course: str = course

    def validate(self, user: User) -> Tuple[bool, list[str]]:
        """ Returns True if the user is taking these courses in the same term """
        valid = user.has_taken_course(self.course) or user.is_taking_course(self.course)
        return valid, ([] if valid else [f'Corequisite: {self.course}'])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # same as courseCondition, but also allow for the course to be the same as the given course
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var <= course_variable)] if condition_var is not None else [model.AddBoolAnd(False)]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var > course_variable)] if condition_var is not None else [model.AddBoolAnd(True)]

    def is_path_to(self, course: str) -> bool:
        return self.course == course

    def __str__(self) -> str:
        return json.dumps({
            'id': self.course
        })

class UOCCondition(Condition):
    """ UOC conditions such as `24UOC in COMP` """

    def __init__(self, uoc: int):
        self.uoc = uoc

        # The conditional uoc category attached to this object.
        # If there is a cateogry, UOC must be from within this category. E.g.
        # COMPA1 - courses within COMPA1
        # SENG - course codes starting with SENG
        # L4 - level 4 courses
        # L2 MATH - level 2 courses starting with MATH
        # CORES - core courses
        # L2 CORES - level 2 core courses
        # And more...
        self.category: Category = AnyCategory()

    def is_path_to(self, course: str) -> bool:
        return False

    def set_category(self, category_classobj: Category):
        """ sets a category for UOC that is counted """
        self.category = category_classobj

    def validate(self, user: User) -> tuple[bool, list[str]]:
        uoc_met = user.uoc(self.category) >= self.uoc
        category = re.sub(r"courses && ([A-Z]{4}) courses", r"\1 courses", str(self.category))
        return uoc_met, ([] if uoc_met else [f"{self.uoc} UOC required in {category} you have {user.uoc(self.category)} UOC"])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # find courses which match definition
        filtered_courses = [course for course in courses if self.category.match_definition(course[1].name)]
        total_filtered_uoc = sum(filtered_course[1].uoc for filtered_course in filtered_courses)
        total_uoc_allowable_after_course = total_filtered_uoc - self.uoc
        # we check if there are
        # 1. enough courses matching our definition to feasibly meet the condition (ie self.uoc courses have been selected)
        # 2. these courses don't come too late in the degree.
        #    There must be at most total_filtered_uoc - self.uoc after the course, or else you didnt complete enough UoC yet

        # we need to do this because OR Tools doesnt allow for checking capacity is >=
        if total_uoc_allowable_after_course < 0:
            return [model.AddBoolAnd(False)]
        boolean_indexes = []
        for variable, _ in filtered_courses:
            # b is a 'channeling constraint'. This is done to fill the resovoir only *if* the course is after or at the same term as the course
            # https://developers.google.com/optimization/cp/channeling
            b = model.NewBoolVar('hi')
            model.Add(variable >= course_variable).OnlyEnforceIf(b)
            model.Add(variable < course_variable).OnlyEnforceIf(b.Not())
            boolean_indexes.append(b)
        return [
            model.AddReservoirConstraintWithActive(
                (course[0] for course in filtered_courses),  # the variables of the filtered courses
                (var[1].uoc for var in filtered_courses),  # can fill the resovoir by some UOC
                boolean_indexes,  # if it comes after the course given
                0,
                total_uoc_allowable_after_course  # until a certain point, or fail the constraint
            )
        ]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        filtered_courses = [course for course in courses if self.category.match_definition(course[1].name)]

        total_filtered_uoc = sum(filtered_course[1].uoc for filtered_course in filtered_courses)
        if total_filtered_uoc < self.uoc:
            return [model.AddBoolAnd(True)]  # if we already dont have enough UOC to meet it, our job is already done

        boolean_indexes = []
        for variable, _ in filtered_courses:
            # b is a 'channeling constraint'. This is done to fill the resovoir only *if* the course is before the course's term
            # https://developers.google.com/optimization/cp/channeling
            b = model.NewBoolVar('hi')
            model.Add(variable < course_variable).OnlyEnforceIf(b)
            model.Add(variable >= course_variable).OnlyEnforceIf(b.Not())
            boolean_indexes.append(b)
        return [
            model.AddReservoirConstraintWithActive(
                (course[0] for course in filtered_courses),  # the variables of the filtered courses
                (var[1].uoc for var in filtered_courses),  # can fill the resovoir by some UOC
                boolean_indexes,  # if it comes before the course given
                0,
                self.uoc  # until a certain point, or fail the constraint
            )
        ]



    def __str__(self) -> str:
        return json.dumps({
            'UOC': self.uoc,
            'category': str(self.category)
        })


class WAMCondition(Condition):
    """ Handles WAM conditions such as 65WAM and 80WAM in """
    def __init__(self, wam: int):
        self.wam = wam

        # The conditional wam category attached to this object.
        # If a category is attached, then the WAM must be from within this category. E.g.
        # 80WAM in COMP
        self.category: Category = AnyCategory()

    def set_category(self, category_classobj: Category):
        """ Set own category to the one given """
        self.category = category_classobj

    def is_path_to(self, course: str) -> bool:
        return False

    def validate(self, user: User) -> tuple[bool, list[str]]:
        wam, marks_complete = user.wam(self.category)
        warning = self.get_warning(wam, marks_complete)

        # If the user has not entered their marks, we allow the course to be unlocked and just display warning as info instead
        return not marks_complete or warning is None, [warning] if warning is not None else []

    def get_warning(self, wam: Optional[float], marks_complete: bool) -> str | None:
        """ Returns an appropriate warning message or None if not needed """
        category = re.sub(r"courses && ([A-Z]{4}) courses", r"\1 courses", str(self.category))
        wam_warning = f"Requires {self.wam} WAM in {category}. "
        if not marks_complete:
            return f"{wam_warning} Your WAM in {category} has not been recorded"

        # Any string returned here should be a warning (i.e. course is not unlocked)
        if wam is None:
            return wam_warning
        if wam >= self.wam:
            return None
        return f"{wam_warning} Your WAM in {category} is currently {wam:.3f}"

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # straight up true or false if the user's current wam supports the course
        return super().condition_to_model(model, user, courses, course_variable)

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        return super().condition_negation(model, user, courses, course_variable)

    def __str__(self) -> str:
        return json.dumps({
            'wam': self.wam,
            'category': str(self.category)
        })


class GradeCondition(Condition):
    """ Handles Grade conditions such as 65GRADE and 80GRADE in [A-Z]{4}[0-9]{4} """

    def __init__(self, grade: int, course: str):
        self.grade = grade
        self.course = course

    def is_path_to(self, course: str) -> bool:
        return self.course == course

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        course_grade = user.get_grade(self.course)
        if course_grade and course_grade < self.grade:
            # if you have already failed to meet it, gg
            return super().condition_to_model(model, user, courses, course_variable)
        condition_var = get_variable(courses, self.course)
        # we cant predict what your mark is, so we just treat it like a CourseCondition
        return [model.Add(condition_var < course_variable)] if condition_var is not None else [model.AddBoolAnd(False)]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        course_grade = user.get_grade(self.course)
        if course_grade and course_grade >= self.grade:
            # if you already beat it, gg
            return super().condition_negation(model, user, courses, course_variable)
        condition_var = get_variable(courses, self.course)
        # we cant predict what your mark is, so we just treat it like a CourseCondition
        return [model.Add(condition_var >= course_variable)] if condition_var is not None else [model.AddBoolAnd(True)]

    def validate(self, user: User) -> tuple[bool, list[str]]:
        if self.course not in user.courses:
            return False, [f"Need {self.grade} in {self.course} for this course"]

        user_grade = user.get_grade(self.course)
        if user_grade is None:
            return True, [f"Requires {self.grade} mark in {self.course}. Your mark has not been recorded"]
        if user_grade < self.grade:
            return False, [f"Your grade {user_grade} in course {self.course} does not meet the grade requirements (minimum {self.grade}) for this course"]
        return True, []

    def __str__(self) -> str:
        return json.dumps({
            'grade': self.grade,
            'course': self.course
        })


class CoresCondition(Condition):
    """ Handles Core Course conditions such as L1 CORES """

    def __init__(self):
        """ the subset of courses in CORES that must be completed """
        self.category: Category = AnyCategory()

    def set_category(self, category_classobj: Category):
        """ Set own category to the one given """
        self.category = category_classobj

    def is_path_to(self, course: str) -> bool:
        return self.category.match_definition(course)

    def validate(self, user: User) -> tuple[bool, list[str]]:
        res = user.completed_core(self.category)
        return res, ([] if res else [f'you have not completed your {self.category} cores'])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        course_names = [var[0].Name() for var in courses]
        does_match, relevant_courses = user.matches_core(course_names, self.category)
        if not does_match:
            # if you can never match the core, gg
            return [model.AddBoolAnd(False)]
        # else we find the relevant courses and assert that they need to happen first
        return [
            model.Add(var < course_variable)
            for course in relevant_courses
            if (var := get_variable(courses, course)) is not None
        ]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        course_names = [var[0].Name() for var in courses]
        does_match, relevant_courses = user.matches_core(course_names, self.category)
        if not does_match:
            # if you cant match the core, youre good
            return [model.AddBoolAnd(True)]

        or_constraints: list[cp_model.Constraint] = [
            model.Add(var >= course_variable)
            for course in relevant_courses
            if (var := get_variable(courses, course)) is not None
        ]
        or_opposite_constraints: list[cp_model.Constraint] = [
            model.Add(var < course_variable)
            for course in relevant_courses
            if (var := get_variable(courses, course)) is not None
        ]
        boolean_vars = [model.NewBoolVar("hi") for _ in or_constraints]
        for constraint, negation, boolean in zip(or_constraints, or_opposite_constraints, boolean_vars):
            # b is a 'channeling constraint'. This is done to allow us to check that at least 1 of these is true
            # https://developers.google.com/optimization/cp/channeling
            constraint.OnlyEnforceIf(boolean)
            negation.OnlyEnforceIf(boolean.Not())
        model.AddBoolOr(boolean_vars)
        return or_constraints

    def __str__(self) -> str:
        return json.dumps({
            'cores': None,
            'category': str(self.category)
        })

class ProgramCondition(Condition):
    """ Handles Program conditions such as 3707 """

    def __init__(self, program: str):
        self.program = program

    def is_path_to(self, course: str) -> bool:
        return False

    def validate(self, user: User) -> tuple[bool, list[str]]:
        valid = user.in_program(self.program)
        return valid, ([] if valid else [f'Program required: {self.program}'])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # just add straight up true or false
        return super().condition_to_model(model, user, courses, course_variable)

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        return super().condition_negation(model, user, courses, course_variable)

    def __str__(self) -> str:
        return json.dumps({
            'program': self.program,
        })


class ProgramTypeCondition(Condition):
    """
    Handles program type conditions, which specify that your program has to
    be some collection of programs.
    for example - be enrolled in Actuarial studies implies that your
    program must be any one of a few programs (actl + double degree codes).
    """

    def __init__(self, programType: str):
        self.programType = programType

    def is_path_to(self, course: str) -> bool:
        return False

    def validate(self, user: User) -> tuple[bool, list[str]]:
        valid = user.program in CACHED_PROGRAM_MAPPINGS[self.programType]
        return user.program in CACHED_PROGRAM_MAPPINGS[self.programType], ([] if valid else [f'you need to do a program of type {self.programType[0:4]}'])

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # just add straight up true or false
        return super().condition_to_model(model, user, courses, course_variable)

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        return super().condition_negation(model, user, courses, course_variable)

    def __str__(self) -> str:
        return json.dumps({
            'programType': self.programType,
        })


class SpecialisationCondition(Condition):
    """ Handles Specialisation conditions such as COMPA1 """

    def __init__(self, specialisation: str):
        self.specialisation = specialisation

    def validate(self, user: User) -> tuple[bool, list[str]]:
        valid = user.in_specialisation(self.specialisation)
        return valid, ([] if valid else [f'Specialisation required: {self.specialisation}'])

    def is_path_to(self, course: str) -> bool:
        return False

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # just add straight up true or false
        return super().condition_to_model(model, user, courses, course_variable)

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        return super().condition_negation(model, user, courses, course_variable)

    def __str__(self) -> str:
        return json.dumps({
            'specialisation': self.specialisation,
        })


class CourseExclusionCondition(Condition):
    """ Handles when you cant take a certain course. Eg Exclusion: MATH1131 for MATH1141"""

    def __init__(self, course: str):
        self.course = course

    def validate(self, user: User) -> tuple[bool, list[str]]:

        is_valid = not (user.has_taken_specific_course(self.course) or user.is_taking_specific_course(self.course))
        return is_valid, ([] if is_valid else [f"Exclusion: {self.course}"])

    def is_path_to(self, course: str) -> bool:
        return False

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var >= course_variable)] if condition_var is not None else [model.AddBoolAnd(True)]

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        condition_var = get_variable(courses, self.course)
        return [model.Add(condition_var < course_variable)] if condition_var is not None else [model.AddBoolAnd(False)]

    def __str__(self) -> str:
        return json.dumps({
            'exclusion': self.course,
        })


class ProgramExclusionCondition(Condition):
    """
    Handles when you can't be in a program to take a course, such as
    taking a genEd course in your own faculty
    """

    def __init__(self, exclusion: str):
        self.exclusion = exclusion

    def validate(self, user: User) -> tuple[bool, list[str]]:
        excluded = not user.in_program(self.exclusion)
        return (excluded, []) if excluded else (excluded, ["This course cannot be taken in your program"])

    def is_path_to(self, course: str) -> bool:
        return False

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        # just add straight up true or false
        return super().condition_to_model(model, user, courses, course_variable)

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        return super().condition_negation(model, user, courses, course_variable)

    def __str__(self) -> str:
        return json.dumps({
            'programExclusion': self.exclusion,
        })


class CompositeCondition(Condition):
    """ Handles AND/OR clauses comprised of condition objects. """

    def __init__(self, logic: Logic = Logic.AND):
        self.conditions: list[Condition] = []
        self.logic = logic

    def add_condition(self, condition: Condition):
        """ Adds a condition object """
        self.conditions.append(condition)

    def set_logic(self, logic: Logic):
        """ AND or OR """
        self.logic = logic

    def condition_to_model(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        if len(self.conditions) == 0:
            return []

        match self.logic:
            case Logic.AND:
                # just aggregate the conditions together, they are already all simutaneously asserted
                return sum((condition.condition_to_model(model, user, courses, course_variable) for condition in self.conditions), [])
            case Logic.OR:
                or_constraints: list[cp_model.Constraint] = sum((
                    condition.condition_to_model(model, user, courses, course_variable)
                    for condition in self.conditions
                ), [])
                or_opposite_constraints: list[cp_model.Constraint] = sum((condition.condition_negation(model, user, courses, course_variable) for condition in self.conditions), [])
                boolean_vars = [model.NewBoolVar("hi") for _ in or_constraints]
                # boolean_vars are a 'channeling constraint'. This is done to allow us to check that at least 1 of these is true
                # https://developers.google.com/optimization/cp/channeling
                for constraint, negation, boolean in zip(or_constraints, or_opposite_constraints, boolean_vars):
                    constraint.OnlyEnforceIf(boolean)
                    negation.OnlyEnforceIf(boolean.Not())
                model.AddBoolOr(boolean_vars)
                return or_constraints

    def condition_negation(self, model: cp_model.CpModel, user: User, courses: list[Tuple[cp_model.IntVar, Course]], course_variable: cp_model.IntVar) -> list[cp_model.Constraint]:
        if len(self.conditions) == 0:
            # still ignore empty composite conditions
            return []

        if self.logic == Logic.OR:
            # opposite of OR is NAND
            return sum((condition.condition_negation(model, user, courses, course_variable) for condition in self.conditions), [])

        # opposite of AND is NOR - at least one must be false
        and_constraints: list[cp_model.Constraint] = sum((condition.condition_negation(model, user, courses, course_variable) for condition in self.conditions), [])
        and_opposite_constraints: list[cp_model.Constraint] = sum((condition.condition_to_model(model, user, courses, course_variable) for condition in self.conditions), [])
        boolean_vars = [model.NewBoolVar("hi") for _ in and_constraints]
        for constraint, negation, boolean in zip(and_constraints, and_opposite_constraints, boolean_vars):
            constraint.OnlyEnforceIf(boolean)
            negation.OnlyEnforceIf(boolean.Not())
        model.AddBoolOr(boolean_vars)
        return and_constraints

    def validate(self, user: User) -> tuple[bool, list[str]]:
        """
        Validate user conditions and return the validated conditions and
        warnings
        """
        if not self.conditions:
            return True, []

        validations = [cond.validate(user) for cond in self.conditions]
        # unzips a zipped list - https://www.geeksforgeeks.org/python-unzip-a-list-of-tuples/
        unlocked, all_warnings = list(zip(*validations))
        wam_warning: list[str] = sum((warning for unlocked_cond, warning in validations if unlocked_cond), [])

        if self.logic == Logic.AND:
            satisfied = all(unlocked)
            return satisfied, (wam_warning if satisfied else ['(' + ' AND '.join(sum(all_warnings,[])) + ')'])  # warnings are flattened

        satisfied = any(unlocked)
        return satisfied, (wam_warning if satisfied else ['(' + ' OR '.join(sum(all_warnings,[])) + ')'])

    def is_path_to(self, course: str) -> bool:
        return any(condition.is_path_to(course) for condition in self.conditions)

    def beneficial(self, user: User, course: dict[str, Tuple[int, Optional[int]]]) -> bool:
        course_name = list(course.keys())[0]
        if self.validate(user)[0] or user.has_taken_course(course_name):
            return False
        return any(condition.beneficial(user, course) for condition in self.conditions)

    def __str__(self, id='start') -> str:
        data: CompositeJsonData = {
            'logic': "and" if self.logic == Logic.AND else "or",
            'id': id,
            'children': []
        }

        for index, cond in enumerate(self.conditions):
            if id == 'start':
                child_index = 'root'
            elif id == 'root':
                child_index = f'subtree.{index}'
            else:
                child_index = f'{id}.{index}'
            if isinstance(cond, CompositeCondition):
                data['children'].append(json.loads(cond.__str__(child_index)))
            else:
                data['children'].append(json.loads(str(cond)))
        return json.dumps(data)
