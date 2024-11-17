from typing import TypedDict

from typing_extensions import Literal, NotRequired


class ProgramContainer(TypedDict):
    type: NotRequired[str]
    courses: NotRequired[dict[str, str | list[str]]]
    title: str
    credits_to_complete: NotRequired[int]
    levels: NotRequired[list[int]]
    notes: str

class SpecData(TypedDict):
    is_optional: bool
    specs: dict[str, str]
    notes: str

class SpecsData(TypedDict):
    honours: NotRequired[dict[str, SpecData]]
    minors: NotRequired[dict[str, SpecData]]
    majors: NotRequired[dict[str, SpecData]]

class Components(TypedDict):
    non_spec_data: list[ProgramContainer]
    spec_data: SpecsData

class Program(TypedDict):
    title: str
    code: str
    duration: NotRequired[int]
    UOC: int
    faculty: str
    overview: str
    structure_summary: str
    components: Components
    processing_warnings: list[str]

class CourseContainer(ProgramContainer):
    core: bool

class CourseConstraint(TypedDict):
    title: str
    description: str

class Specialisation(TypedDict):
    programs: list[str]
    name: str
    type: Literal["major"] | Literal["minor"] | Literal["honours"]
    UOC: int
    code: str
    course_constraints: list[CourseConstraint]
    curriculum: list[CourseContainer]

class Course(TypedDict):
    title: str
    code: str
    UOC: int
    level: int
    description: str
    study_level: Literal["Undergraduate"] | Literal["Postgraduate"]
    school: str
    faculty: str
    campus: Literal["Sydney"] | Literal["UNSW Canberra"] | Literal["Paddington"] | Literal[""]
    equivalents: dict[str, Literal[1]]
    exclusions: dict[str, Literal[1]]
    terms: list[Literal["T1"] | Literal["T2"] | Literal["T3"] | Literal["T0"]]
    gen_ed: bool
    raw_requirements: str
    is_multiterm: bool
