"""
Contains `ProgramRestrictions` and relevant sub-classes
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from algorithms.objects.categories import Category
from algorithms.objects.conditions import Condition
from algorithms.objects.helper import Logic
from algorithms.objects.user import User


class ProgramRestriction(ABC):
    """
    Abstract class for program restrictions
    """

    # TODO: In the long-run (imo), we should stop passing courses around as
    # just strings. Rather, they should be self-contained objects that
    # contain all their information (e.g. course code, name, Conditions)
    # Removes the need for this class to know how to fetch conditions
    @abstractmethod
    def validate_course_allowed(self, user: User, course: str) -> bool:
        """
        Returns whether or not the course is allowed.
        Future possibility: Also return back a str of why it may not
        be allowed
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()

class CompositeRestriction(ProgramRestriction):
    """
    A composite restriction is a restriction that is made up of other
    restrictions. It is used to combine restrictions together.
    """

    def __init__(self, logic: Logic=Logic.AND, restrictions: Optional[List[ProgramRestriction]]=None):
        self.restrictions = restrictions if restrictions is not None else []
        self.logic = logic


    def validate_course_allowed(self, user: User, course: str) -> bool:
        """
        Returns whether or not the course is allowed.
        Future possibility: Also return back a str of why it may not
        be allowed.
        """
        match self.logic:
            case Logic.AND:
                return all(
                    restriction.validate_course_allowed(user, course)
                    for restriction in self.restrictions
                )
            case Logic.OR:
                return any(
                    restriction.validate_course_allowed(user, course)
                    for restriction in self.restrictions
                )
            case _:
                # Should never actually happen as the above cases are exhaustive
                raise ValueError(f"Unknown logic: {self.logic}")

    def set_logic(self, logic: Logic):
        """ Set the logic of the composite restriction"""
        self.logic = logic

    def is_restriction_free(self) -> bool:
        """Returns whether or not the composite restriction is empty"""
        return len(self.restrictions) == 0

    def add_restriction(self, restriction: ProgramRestriction):
        """Add an aditional category to the composite restriction"""
        self.restrictions.append(restriction)

    def __str__(self) -> str:
        return f"CompositeRestriction: Logic::({self.logic}) Restrictions::({[str(restriction) for restriction in self.restrictions]})"

class NoRestriction(ProgramRestriction):
    """
    Will always allow a course to be taken. Does not enforce any conditins.
    """

    def __init__(self) -> None:
        pass

    def validate_course_allowed(self, user: User, course: str) -> bool:
        del user, course
        return True

    def __str__(self) -> str:
        return "NoRestriction"


class MaturityRestriction(ProgramRestriction):
    """
    Models the `Maturity Requirement` wherein, a certain condition (dependancy)
    must be achieved before a course from a given Category (dependent) can be taken.
    """

    def __init__(self, dependency: Condition, dependent: Category):
        self.dependency = dependency
        self.dependent = dependent

    def match_dependent(self, course: str) -> bool:
        """
        Check if the given course is a match for the category defined in the dependent
        """
        return self.dependent.match_definition(course)

    def dependency_met(self, user: User) -> bool:
        """ Wrapper to validate `dependency` as just a boolean """
        return self.dependency.validate(user)[0]

    def validate_course_allowed(
            self, user: User, course: str,
        ) -> bool:
        """
        Validate whether a user can do the given course.
        Can not be done iff there is a match on dependent and dependency is not met
        """
        return not (self.match_dependent(course) and not self.dependency_met(user))

    def beneficial(self, user: User, course: dict[str, Tuple[int, int | None]]) -> bool:
        """
        Will a course be beneficial to advancing this condition?
        More specifically, can the course be used to meet the dependency?
        """
        return self.dependency.beneficial(user, course)

    def __str__(self) -> str:
        return (
            f"MaturityCondition: Dependency: {self.dependency}, self.dependent: {self.dependent}"
        )

class CourseRestriction(ProgramRestriction):
    """
    For when a certain course is disallowed by the program
    """

    def __init__(self, course: str):
        self.course = course

    def validate_course_allowed(self, user: User, course: str) -> bool:
        return course != self.course

    def __str__(self) -> str:
        return f"CourseRestriction: {self.course}"

class CategoryUOCRestriction(ProgramRestriction):
    """
    For when a user is only allowed to do a max uoc of some category.,
    Ex: May only do 56 UOC of Level 1 Courses
    """

    def __init__(self, uoc: int, category: Category) -> None:
        self.category: Category = category
        self.uoc_allowed: int = uoc

    def validate_course_allowed(self, user: User, course: str, course_uoc: int=6) -> bool:
        """
        A user cannot do the course if:
            - Course matches the category
            - User has already done max uoc of the category
        """
        if not self.category.match_definition(course):
            return True
        uoc_completed: int = sum(
            uoc for _, uoc in user.get_courses_with_uoc()
        )
        return uoc_completed + course_uoc <= self.uoc_allowed

    def __str__(self) -> str:
        return f"CategoryUOCRestriction: {self.uoc_allowed} UOC of {self.category}"

class CategoryRestriction(ProgramRestriction):
    """
    User is disallowed from doing a course from certain category.
    EX: You may not take courses from a certain faculty.
    """

    def __init__(self, category: Category) -> None:
        self.category = category

    def validate_course_allowed(self, user: User, course: str) -> bool:
        """
        A user cannot do the course if:
            - Course matches the category
        """
        del user
        return not self.category.match_definition(course)

    def __str__(self) -> str:
        return f"CategoryRestriction: {self.category}"
