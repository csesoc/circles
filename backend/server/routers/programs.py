"""
API for fetching data about programs and specialisations """
import functools
from contextlib import suppress
from typing import Any, Callable, Dict, List, Optional

from fastapi import APIRouter
from server.db.mongo.conn import programsCOL
from server.routers.utility.manual_fixes import apply_manual_fixes
from server.routers.model import (CourseCodes, Courses, CoursesPathDict, Graph, Programs, Structure, StructureContainer,
                                  StructureDict)
from server.routers.utility.common import add_program_code_details_to_structure, add_specialisations_to_structure, convert_adj_list_to_edge_list, get_core_courses, get_gen_eds, get_incoming_edges, get_program_structure, prune_edges

router = APIRouter(
    prefix="/programs",
    tags=["programs"],
)


@router.get("/")
def programs_index() -> str:
    """ sanity test that this file is loaded """
    return "Index of programs"


# TODO: response model to this somehow
@router.get("/getAllPrograms")
def get_all_programs() -> Dict[Any, Any]:
    """
    Like `/getPrograms` but does not filter any programs for if they are
    production ready.
    """
    return {
        "programs": {
            q["code"]: q["title"]
            for q in programsCOL.find()
        }
    }

@router.get(
    "/getPrograms",
    response_model=Programs,
    responses={
        200: {
            "description": "Returns all programs",
            "content": {
                "application/json": {
                    "example": {
                        "programs": {
                            "3502": "Commerce",
                            "3707": "Engineering (Honours)",
                            "3778": "Computer Science",
                            "3970": "Science",
                        }
                    }
                }
            },
        }
    },
)
def get_programs() -> dict[str, dict[str, str]]:
    """ Fetch all the programs the backend knows about in the format of { code: title } """
    # return {"programs": {q["code"]: q["title"] for q in programsCOL.find()}}
    return {
        "programs": {
            # "3362": "City Planning (Honours)",
            "3778": "Computer Science",
            "3779": "Advanced Computer Science (Honours)",
            "3502": "Commerce",
            "3970": "Science",
            "3543": "Economics",
            "3707": "Engineering (Honours)",
            "3784": "Commerce / Computer Science",
            "3789": "Science / Computer Science",
            "3785": "Engineering (Honours) / Computer Science",
            "3673": "Economics / Computer Science"
        }
    }

@router.get(
    "/getStructure/{programCode}/{spec}",
    response_model=Structure,
    responses={
        400: { "description": "Uh oh you broke me" },
        200: {
            "description": "Returns the program structure",
            "content": {
                "application/json": {
                    "example": {
                        "Major - COMPS1 - Computer Science": {
                            "name": "Database Systems",
                            "content": {
                                "Core Courses": {
                                    "UOC": 66,
                                    "courses": {
                                        "COMP3821": "Extended Algorithms and Programming Techniques",
                                        "COMP3121": "Algorithms and Programming Techniques",
                                    },
                                },
                                "Computing Electives": {
                                    "UOC": 30,
                                    "courses": {
                                        "ENGG4600": "Engineering Vertically Integrated Project",
                                        "ENGG2600": "Engineering Vertically Integrated Project",
                                    },
                                },
                            },
                            "notes": "Students must take 30 UOC of the following courses.",
                        },
                        "Major - FINSA1 - Finance": {
                            "name": "Finance",
                            "content": {
                                "Core Courses": {
                                    "UOC": 66,
                                    "courses": {
                                        "FINS3121": "Financial Accounting",
                                    },
                                },
                            },
                            "notes": "Students must take 60 UOC of the following courses.",
                        },
                        "Minor - FINSA2 - Finance": {
                            "name": "Finance",
                            "content": {
                                "Prescribed Electives": {
                                    "UOC": 12,
                                    "courses": {
                                        "FINS3616": "International Business Finance",
                                        "FINS3634": "Credit Analysis and Lending",
                                    },
                                },
                                "Core Courses": {
                                    "UOC": 18,
                                    "courses": {
                                        "FINS2613": "Intermediate Business Finance",
                                        "COMM1180": "Value Creation",
                                        "FINS1612": "Capital Markets and Institutions",
                                    },
                                },
                            },
                            "notes": "Students must take 12 UOC of the following courses.",
                        },
                        "General": {
                            "name": "General Program Requirements",
                            "content": {
                                "General Education": {"UOC": 12},
                                "FlexEducation": {"UOC": 6},
                                "BusinessCoreCourses": {
                                    "UOC": 6,
                                    "courses": {"BUSI9999": "How To Business"},
                                },
                            }
                        },
                    }
                }
            }
        }
    }
)
@router.get("/getStructure/{programCode}", response_model=Structure)
def get_structure(
    programCode: str, spec: Optional[str] = None, ignore: Optional[str] = None
) -> StructureDict:
    """ get the structure of a course given specs and program code """

    ignored = ignore.split("+") if ignore else []
    specs = spec.split("+") if spec else []

    structure, uoc = get_program_structure(programCode, specs=specs, ignored=ignored)

    return {
        "structure": structure,
        "uoc": uoc,
    }

@router.get("/getStructureCourseList/{programCode}/{spec}", response_model=CourseCodes)
@router.get("/getStructureCourseList/{programCode}", response_model=CourseCodes)
def get_structure_course_list(
        programCode: str, spec: Optional[str] = None
):
    """
        Similar to `/getStructure` but, returns a raw list of courses with no further
        nesting or categorisation.
        TODO: Add a test for this.
    """
    structure: dict[str, StructureContainer] = {}
    specs = spec.split("+") if spec is not None else []

    structure = add_specialisations_to_structure(structure, specs)
    structure, _ = add_program_code_details_to_structure(structure, programCode)
    apply_manual_fixes(structure, programCode)

    return {
        "courses": course_list_from_structure(structure),
    }

@router.get(
    "/getGenEds/{programCode}",
    response_model=Courses,
    responses={
        400: {
            "description": "The given program code could not be found in the database",
        },
        200: {
            "description": "Returns all geneds available to a given to the given code",
            "content": {
                "application/json": {
                    "example": {
                        "courses": {
                            "ACTL3142": "Statistical Machine Learning for Risk and Actuarial Applications",
                            "ACTL4305": "Actuarial Data Analytic Applications",
                            "ADAD2610": "Art and Design for Environmental Challenges",
                            "ANAT2521": "Biological Anthropology: Principles and Practices",
                            "ARTS1010": "The Life of Words"
                        }
                    }
                }
            },
        },
    },
)
def get_gen_eds_route(programCode: str) -> Dict[str, Dict[str, str]]:
    """ Fetches the geneds for a given program code """
    course_list: List[str] = course_list_from_structure(get_program_structure(programCode, ignored=["gened"])[0])
    return get_gen_eds(programCode, course_list)

@router.get("/graph/{programCode}/{spec}", response_model=Graph)
@router.get("/graph/{programCode}", response_model=Graph)
def graph(
        programCode: str, spec: Optional[str] = None
    ):
    """
    Constructs a structure for the frontend to use for the graphical
    selector.
    Returns back a list of directed edges where u -> v => u in v's
    prereqs or coreqs.
    Returns:
        "edges" :{
            [
                {
                    "source": (str) "CODEXXXX",
                    "target": (str) "CODEXXXX",
                }
            ]
        },
    No longer returns 'err_edges: failed_courses' as those are suppressed and
    caught by the processor
    """
    courses = get_structure_course_list(programCode, spec)["courses"]

    proto_edges: list[CoursesPathDict] = [
        {
            "original": course,
            "courses": get_incoming_edges(course)
        }
        for course in courses
    ]

    edges = prune_edges(
        convert_adj_list_to_edge_list(proto_edges),
        courses
    )

    return {
        "edges": edges,
        "courses": courses,
    }

@router.get("/getCores/{programCode}/{spec}")
def get_cores(programCode: str, spec: str):
    return get_core_courses(programCode, spec.split('+'))

###############################################################
#                       End of Routes                         #
###############################################################


def course_list_from_structure(structure: Dict[str, StructureContainer]) -> list[str]:
    """
        Given a formed structure, return the list of courses
        in that structure.
        TODO: The `__recursive_course_search` should be deprecated
        due to better type definitions of `StructureDict`
    """
    courses = []
    def __recursive_course_search(structure: dict) -> None:
        """
            Recursively search for courses in a structure. Add
            courses found to `courses` object in upper group.
        """
        if not isinstance(structure, (list, dict)):
            return
        for k, v in structure.items():
            with suppress(KeyError):
                if not isinstance(v, dict) or "rule" in v["type"]:
                    continue
            if "courses" in k:
                courses.extend(v.keys())
            __recursive_course_search(v)
        return
    __recursive_course_search(dict(structure))
    return courses

def compose(*functions: Callable) -> Callable:
    """
        Compose a list of functions into a single function.
        The functions are applied in the order they are given.
    """
    return functools.reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), functions)
