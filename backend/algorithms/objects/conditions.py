'''
Contains the Conditions classes
'''
import abc
from enum import Enum, auto
import json
from algorithms.objects.categories import AnyCategory

'''Keywords'''
class Logic(Enum):
    AND = auto()
    OR = auto()

'''CACHED'''
CACHED_CONDITIONS_TOKENS_PATH = "./data/final_data/conditionsTokens.json"
with open(CACHED_CONDITIONS_TOKENS_PATH) as f:
    CACHED_CONDITIONS_TOKENS = json.load(f)


CACHED_PRGORAM_MAPPINGS_FILE = "./algorithms/cache/programMappings.json"
with open(CACHED_PRGORAM_MAPPINGS_FILE) as f:
    CACHED_PRGORAM_MAPPINGS = json.load(f)

class Condition():
    @abc.abstractmethod
    def validate(self, user) -> tuple[bool, list[str]]:
        '''
        returns a tuple first containing whether or not the course is unlocked,
        and second any warnings about the course's unlocked state - eg that the course
        needs some wam that the student has not entered.
        '''
        pass

class CourseCondition(Condition):
    '''Condition that the student has completed this course before the current term'''

    def __init__(self, course):
        self.course = course

    def validate(self, user) -> tuple[bool, list[str]]:
        return user.has_taken_course(self.course), []


class CoreqCoursesCondition(Condition):
    """Condition that the student has completed the course/s in or before the current term"""

    def __init__(self, logic: Logic=Logic.AND):
        # An example corequisite is [COMP1511 || COMP1521 || COMP1531]. The user
        # must have taken one of these courses either before or in the current term
        self.courses: list[str] = []
        self.logic: Logic = logic

    def add_course(self, course: str):
        self.courses.append(course)

    def set_logic(self, logic: Logic):
        self.logic = logic

    def validate(self, user) -> tuple[bool, list[str]]:
        """Returns true if the user is taking these courses in the same term"""
        match self.logic:
            case Logic.AND:
                return all(user.has_taken_course(course) or user.is_taking_course(course) for course in self.courses), []
            case Logic.OR:
                return any(user.has_taken_course(course) or user.is_taking_course(course) for course in self.courses), []

        print("Conditions Error: validation was not of type AND or OR")
        return True, []


class UOCCondition(Condition):
    '''UOC conditions such as "24UOC in COMP"'''

    def __init__(self, uoc):
        self.uoc = uoc

        # The conditional uoc category attached to this object.
        # If there is a cateogry, UOC must be from within this category. E.g.
        # COMPA1 - courses within COMPA1
        # SENG - course codes starting with SENG
        # L4 - level 4 courses
        # L2 MATH - level 2 courses starting with MATH
        # CORE - core courses
        # And more...
        self.category = AnyCategory()

    def set_category(self, category_classobj):
        self.category = category_classobj

    def validate(self, user) -> tuple[bool, list[str]]:
            return user.uoc(self.category) >= self.uoc, []

class WAMCondition(Condition):
    '''Handles WAM conditions such as 65WAM and 80WAM in'''

    def __init__(self, wam):
        self.wam = wam

        # The conditional wam category attached to this object.
        # If a category is attached, then the WAM must be from within this category. E.g.
        # 80WAM in COMP
        # NOTE: We will convert 80WAM in (COMP || BINH || SENG) to:
        # 80WAM in COMP || 80WAM in BINH || 80WAM in SENG
        # so that only one category is attached to this wam condition
        self.category = AnyCategory()

    def set_category(self, category_classobj):
        self.category = category_classobj

    def validate(self, user) -> tuple[bool, list[str]]:
        '''
        Determines if the user has met the WAM condition for this category.

        Will always return True and a warning since WAM can fluctuate
        '''
        warning = self.get_warning(user.wam(self.category))
        return True, [warning] if warning else []

    def get_warning(self, applicable_wam):
        '''Returns an appropriate warning message or None if not needed'''
        if type(self.category) is AnyCategory:
            if applicable_wam == None:
                return f"Requires {self.wam} WAM. Your WAM has not been recorded"
            elif applicable_wam >= self.wam:
                return None
            else:
                return f"Requires {self.wam} WAM. Your WAM is currently {applicable_wam:.3f}"
        else:
            if applicable_wam == None:
                return f"Requires {self.wam} WAM in {self.category}. Your WAM in {self.category} has not been recorded"
            elif applicable_wam >= self.wam:
                return None
            else:
                return f"Requires {self.wam} WAM in {self.category}. Your WAM in {self.category} is currently {applicable_wam:.3f}"

class GRADECondition(Condition):
    '''Handles GRADE conditions such as 65GRADE and 80GRADE in [A-Z]{4}[0-9]{4}'''

    def __init__(self, grade, course):
        self.grade = grade

        # Course code
        self.course = course

    def validate(self, user) -> tuple[bool, list[str]]:
        if self.course not in user.courses:
            return False, []

        user_grade = user.get_grade(self.course)
        if user_grade == None:
            return True, [self.get_warning()]
        elif user_grade < self.grade:
            return False, []
        else:
            return True, []

    def get_warning(self):
        return f"Requires {self.grade} mark in {self.course}. Your mark has not been recorded"

class ProgramCondition(Condition):
    '''Handles Program conditions such as 3707'''

    def __init__(self, program):
        self.program = program

    def validate(self, user) -> tuple[bool, list[str]]:
        return user.in_program(self.program), []

class ProgramTypeCondition(Condition):
    '''
    Handles program type conditions, which specify that your program has to be some collection of programs.\n
    for example - be enrolled in Actuarial studies implies that your program must be any one of a few programs (actl + double degree codes).\n
    '''
    def __init__(self, programType):
        self.programType = programType
    
    def validate(self, user) -> tuple[bool, list[str]]:
        return user.program in CACHED_PRGORAM_MAPPINGS[self.programType], []

class SpecialisationCondition(Condition):
    '''Handles Specialisation conditions such as COMPA1'''

    def __init__(self, specialisation):
        self.specialisation = specialisation

    def validate(self, user) -> tuple[bool, list[str]]:
        return user.in_specialisation(self.specialisation), []

class CourseExclusionCondition(Condition):
    ''' Handles when you cant take a certain course. Eg Exclusion: MATH1131 for MATH1141'''
    def __init__(self, exclusion):
        self.exclusion = exclusion
    def validate(self, user) -> tuple[bool, list[str]]:
        return not user.has_taken_course(self.exclusion), []

class ProgramExclusionCondition(Condition):
    ''' Handles when you cant be in a program to take a course, such as taking a genEd course in your own faculty'''
    def __init__(self, exclusion):
        self.exclusion = exclusion
    def validate(self, user) -> tuple[bool, list[str]]:
        return not user.in_program(self.exclusion), []

class CompositeCondition(Condition):
    '''Handles AND/OR clauses comprised of condition objects.'''

    def __init__(self, logic: Logic = Logic.AND):
        self.conditions: list[Condition] = []
        self.logic = logic

    def add_condition(self, condition_classobj: Condition):
        '''Adds a condition object'''
        self.conditions.append(condition_classobj)

    def set_logic(self, logic: Logic):
        '''AND or OR'''
        self.logic = logic

    def validate(self, user) -> tuple[bool, list[str]]:
        if self.conditions == []:
            return True, []

        validations = [cond.validate(user) for cond in self.conditions]
        # unzips a zipped list - https://www.geeksforgeeks.org/python-unzip-a-list-of-tuples/
        unlocked, warnings = list(zip(*validations))
        satisfied = all(unlocked) if self.logic == Logic.AND else any(unlocked)

        return satisfied, sum(warnings, []) # warnings are flattened
