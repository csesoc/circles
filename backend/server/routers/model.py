""" model for interacting with the FE """
# pylint: disable=missing-class-docstring
import json
import pickle
from typing import Literal, Optional, TypedDict

from algorithms.objects.conditions import CompositeCondition
from algorithms.objects.user import User
from pydantic import BaseModel


class Programs(BaseModel):
    programs: dict


class Specialisations(BaseModel):
    spec: dict[str, dict]  # cant do more specific because NotRequired doesnt work


class ProgramCourses(BaseModel):
    courses: dict[str, str]


class CourseDetails(BaseModel):
    title: str
    code: str
    UOC: int
    level: int
    description: str
    study_level: str
    school: Optional[str]
    campus: str
    equivalents: dict[str, str]
    raw_requirements: str
    exclusions: dict[str, Literal[1]]
    handbook_note: str
    terms: list[str]
    gen_ed: bool
    is_legacy: bool
    is_accurate: bool
    is_multiterm: Optional[bool]


class ContainerContent(TypedDict):
    UOC: int
    courses: dict[str, str | list[str]]
    type: str
    notes: str

class StructureContainer(TypedDict):
    name: str
    content: dict[str, ContainerContent]

class Structure(BaseModel):
    structure: dict[str, StructureContainer]
    uoc: int


# TODO: This should just take a token now
class UserData(BaseModel):
    program: str
    specialisations: list[str]
    courses: dict


class CourseState(BaseModel):
    is_accurate: bool
    unlocked: bool
    handbook_note: str
    warnings: list


class ValidCourseState(BaseModel):
    is_accurate: bool
    unlocked: bool
    handbook_note: str
    warnings: list
    supressed: bool


class CoursesState(BaseModel):
    courses_state: dict[str, CourseState] = {}


class ValidCoursesState(BaseModel):
    courses_state: dict[str, ValidCourseState] = {}


class CoursesUnlockedWhenTaken (BaseModel):
    direct_unlock: list[str]
    indirect_unlock: list[str]


class CourseTypeState(BaseModel):
    is_accurate: bool
    unlocked: bool
    handbook_note: str
    warnings: list[str]
    course_type: list[str]


class CoursesTypeState(BaseModel):
    courses_state: dict[str, CourseTypeState] = {}


class MostRecentPastTerm(TypedDict):
    Y: int
    T: int


class ValidPlannerData(BaseModel):
    programCode: str
    specialisations: list[str]
    plan: list[list[dict[str, tuple[int, Optional[int]]]]]
    mostRecentPastTerm: MostRecentPastTerm

class PlannerData(BaseModel):
    programCode: str
    specialisations: list[str]
    plan: list[list[dict[str, Optional[list[Optional[int]]]]]]
    mostRecentPastTerm: MostRecentPastTerm
    class Config:
        schema_extra = {
            "example": {
                "program": "3707",
                "specialisations": ["COMPA1"],
                "plan": [
                    [
                        {},
                        {
                            "COMP1511": [6, None],
                            "MATH1141": [6, None],
                            "MATH1081": [6, None],
                        },
                        {
                            "COMP1521": [6, None],
                            "COMP9444": [6, None],
                        },
                        {
                            "COMP2521": [6, None],
                            "MATH1241": [6, None],
                            "COMP3331": [6, None],
                        },
                    ],
                    [
                        {},
                        {
                            "COMP1531": [6, None],
                            "COMP6080": [6, None],
                            "COMP3821": [6, None],
                        },
                    ],
                ],
                "mostRecentPastTerm": {
                    "Y": 1,
                    "T": 0,
                },
            }
        }

    def to_user(self) -> User:
        user = User()
        user.program = self.programCode
        user.specialisations = self.specialisations[:]

        # prevent circular import; TODO: There has to be a better way
        from server.routers.courses import get_course

        for year in self.plan:
            for term in year:
                cleaned_term = {}
                for course_name, course_value in term.items():
                    cleaned_term[course_name] = (
                        (course_value[0], course_value[1]) if course_value
                        else (get_course(course_name)["UOC"], None)
                    )
                user.add_courses(cleaned_term)
        return user


class DegreeLocalStorage(TypedDict):
    programCode: str
    specs: list[str]
    isComplete: bool

class PlannerLocalStorage(TypedDict):
    mostRecentPastTerm: MostRecentPastTerm
    unplanned: list[str]
    startYear: int
    isSummerEnabled: bool
    years: list[dict[str, list[str]]]
    # todo: give `dict` its own params
    courses: dict[str, dict]

LetterGrade = Literal['SY', 'FL', 'PS', 'CR', 'DN', 'HD']
Mark = Optional[int|LetterGrade]

class CoursesStorage(TypedDict):
    code: str
    suppressed: bool
    mark: Mark

class Storage(TypedDict):
    degree: DegreeLocalStorage
    planner: PlannerLocalStorage
    courses: dict[str, CoursesStorage]

class LocalStorage(BaseModel):
    degree: DegreeLocalStorage
    planner: PlannerLocalStorage

class CourseMark(BaseModel):
    course: str
    mark: Mark

class CourseCodes(BaseModel):
    courses: list[str]

class Courses(BaseModel):
    courses: dict[str, str] = {}

class CoursesPath(BaseModel):
    original: str
    courses: list[str]

class CoursesPathDict(TypedDict):
    original: str
    courses: list[str]

class Description(BaseModel):
    description: str

class SpecialisationTypes(BaseModel):
    types: list[str]

class Graph(BaseModel):
    edges: list[dict[str, str]]
    courses: list[str]

class TermsList(BaseModel):
    terms: Optional[dict[str, Optional[list[str]]]]
    # Actually tuple(str, fastapi.exceptions.HTTPException)
    fails: Optional[list[tuple]]

class StructureDict(TypedDict):
    structure: dict[str, StructureContainer]
    uoc: int

# Used in addToUnplanned, removeCourse and unscheduleCourse routes
class CourseCode(BaseModel):
    courseCode: str

# Used in unPlannedToTerm route
class UnPlannedToTerm(BaseModel):
    destRow: int
    destTerm: str
    destIndex: int
    courseCode: str

# used in PlannedToTerm route
class PlannedToTerm(BaseModel):
    srcRow: int
    srcTerm: str
    destRow: int
    destTerm: str
    destIndex: int
    courseCode: str

class ProgramTime(BaseModel):
    startTime: tuple[int, int]  # (Year, Term) start of program
    endTime: tuple[int, int]
    uocMax: list[int]  # list of maximum uocs per term e.g. [12, 20, 20, 20] as in 12 in first term, 20 in each of the next 3 terms

class TermsOffered(TypedDict):
    terms: dict[str, list[str]]
    fails: list[tuple]

CONDITIONS_PATH = "data/final_data/conditions.pkl"
with open(CONDITIONS_PATH, "rb") as file:
    CONDITIONS: dict[str, CompositeCondition] = pickle.load(file)

with open("algorithms/cache/handbook_note.json", "r", encoding="utf8") as handbook_file:
    CACHED_HANDBOOK_NOTE: dict[str, str] = json.load(handbook_file)
