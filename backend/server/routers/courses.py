"""
APIs for the /courses/ route.
"""
import pickle
import re
from contextlib import suppress
from typing import Annotated, Dict, List, Optional, Set, Tuple

from algorithms.create_program import PROGRAM_RESTRICTIONS_PICKLE_FILE
from algorithms.objects.program_restrictions import NoRestriction, ProgramRestriction
from algorithms.objects.user import User
from data.config import ARCHIVED_YEARS
from fastapi import APIRouter, HTTPException, Security
from fuzzywuzzy import fuzz  # type: ignore
from server.routers.utility.sessions.middleware import HTTPBearerToUserID
from server.routers.utility.user import get_setup_user, user_storage_to_algo_user
from server.db.mongo.conn import archivesDB, coursesCOL
from server.routers.model import (CACHED_HANDBOOK_NOTE, CONDITIONS, CourseCodes, CourseDetails, CourseState, CoursesPath,
                                  CoursesPathDict, CoursesState, CoursesUnlockedWhenTaken, ProgramCourses, TermsList,
                                  TermsOffered)
from server.routers.utility.common import get_course_details, get_incoming_edges, get_legacy_course_details, get_program_structure, get_terms_offered_multiple_years

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

require_uid = HTTPBearerToUserID()

# TODO: would prefer to initialise ALL_COURSES here but that fails on CI for some reason
ALL_COURSES: Optional[Dict[str, str]] = None

def fetch_all_courses() -> Dict[str, str]:
    """
    Returns a dictionary of all courses as a key-val pair with:
        key: course code
        value: course_title
    """
    # TODO: with actual bootstrapping, this should be done once and cached
    # without giving anyone else the ability to access the global
    # directly
    global ALL_COURSES
    if ALL_COURSES is not None:
        return ALL_COURSES

    courses = {}
    for course in coursesCOL.find():
        courses[course["code"]] = course["title"]

    for year in sorted(ARCHIVED_YEARS, reverse=True):
        for course in archivesDB[str(year)].find():
            if course["code"] not in courses:
                courses[course["code"]] = course["title"]

    ALL_COURSES = courses

    return ALL_COURSES


def get_all_course_states_for_user(user: User) -> dict[str, CourseState]:
    coursesState: dict[str, CourseState] = {}

    for course, condition in CONDITIONS.items():
        result, warnings = condition.validate(user) if condition is not None else (True, [])
        if result:
            coursesState[course] = CourseState(
                is_accurate=condition is not None,
                unlocked=result,
                handbook_note=CACHED_HANDBOOK_NOTE.get(course, ""),
                warnings=warnings,
            )

    return coursesState


@router.get("/")
def api_index() -> str:
    """ Returns the index of the courses API """
    return "Index of courses"


@router.get("/jsonified/{courseCode}")
def get_jsonified_course(courseCode: str) -> str:
    return str(CONDITIONS[courseCode])

@router.get("/dump")
def get_courses() -> list[Dict]:
    """
    Gets all courses in the database.
    (For CSElectives)
    """

    def generate_course(course, is_legacy):
        course["is_legacy"] = is_legacy
        course.setdefault("school", None)
        del course["_id"]
        with suppress(KeyError):
            del course["exclusions"]["leftover_plaintext"]
        return course

    all_courses = fetch_all_courses()

    courses = {}
    for course in coursesCOL.find():
        courses[course["code"]] = generate_course(course, False)

    years = list(map(str, sorted(ARCHIVED_YEARS, reverse=True)))
    for course_code in all_courses:
        if course_code in courses:
            continue
        for year in years:
            course = archivesDB[year].find_one({"code": course_code})
            if course:
                courses[course["code"]] = generate_course(course, True)
                break

    return list(courses.values())

@router.get(
    "/getCourse/{courseCode}",
    response_model=CourseDetails,
    responses={
        400: {
            "description": "The given course code could not be found in the database",
        },
        200: {
            "description": "Returns all course details to given code",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Programming Fundamentals",
                        "code": "COMP1511",
                        "UOC": 6,
                        "level": 1,
                        "description": """An introduction to problem-solving via programming, which aims to have students develop
                                    proficiency in using a high level programming language. Topics: algorithms, program structures
                                    (statements, sequence, selection, iteration, functions), data types (numeric, character), data structures
                                    (arrays, tuples, pointers, lists), storage structures (memory, addresses), introduction to analysis of
                                    algorithms, testing, code quality, teamwork, and reflective practice. The course includes extensive practical
                                    work in labs and programming projects.</p>\n<p>Additional Information</p>\n<p>This course should be taken by
                                    all CSE majors, and any other students who have an interest in computing or who wish to be extended.
                                    It does not require any prior computing knowledge or experience.</p>\n
                                    <p>COMP1511 leads on to COMP1521, COMP1531, COMP2511 and COMP2521, which form the core of the study of
                                    computing at UNSW and which are pre-requisites for the full range of further computing courses.</p>\n<p>Due to
                                    overlapping material, students who complete COMP1511 may not also enrol in COMP1911 or COMP1921. </p>""",
                        "study_level": "Undergraduate",
                        "school": "School of Computer Science and Engineering",
                        "faculty": "Faculty of Engineering",
                        "campus": "Sydney",
                        "equivalents": {"DPST1091": 1, "COMP1917": 1},
                        "exclusions": {"DPST1091": 1},
                        "terms": ["T1", "T2", "T3"],
                        "raw_requirements": "",
                        "gen_ed": True,
                    }
                }
            },
        },
    },
)
def get_course(courseCode: str):
    """
    Get info about a course given its courseCode
    - start with the current database
    - if not found, check the archives
    """
    result = get_course_details(courseCode)

    result['is_accurate'] = CONDITIONS.get(courseCode) is not None
    result['handbook_note'] = CACHED_HANDBOOK_NOTE.get(courseCode, "")

    return result


@router.post(
    "/searchCourse/{search_string}",
    responses={
        200: {
            "description": "Returns a list of the most relevant courses to a search term",
            "content": {
                "application/json": {
                    "example": {
                            "ACCT1511": "Accounting and Financial Management 1B",
                            "ACCT2542": "Corporate Financial Reporting and Analysis",
                            "ACCT3202": "Industry Placement 2",
                            "ACCT3303": "Industry Placement 3",
                            "ACCT3610": "Business Analysis and Valuation",
                            "ACCT4797": "Thesis (Accounting) B",
                            "ACCT4809": "Current Developments in Auditing Research",
                            "ACCT4852": "Current Developments in Accounting Research - Managerial",
                            "ACCT4897": "Seminar in Research Methodology",
                            "ACTL1101": "Introduction to Actuarial Studies",
                            "ACTL2101": "Industry Placement 1",
                            "ACTL2102": "Foundations of Actuarial Models",
                            "ACTL3142": "Actuarial Data and Analysis",
                    }
                }
            }
        }
    },
)
def search(search_string: str, uid: Annotated[str, Security(require_uid)]) -> Dict[str, str]:
    """
    Search for courses with regex
    e.g. search(COMP1) would return
        { "COMP1511" :  "Programming Fundamentals",
          "COMP1521" : "Computer Systems Fundamentals",
          "COMP1531": "SoftEng Fundamentals",
            ……. }
    """
    all_courses = fetch_all_courses()

    user = get_setup_user(uid)
    specialisations = list(user['degree']['specs'])
    majors = list(filter(lambda x: x.endswith("1") or x.endswith("H"), specialisations))
    minors = list(filter(lambda x: x.endswith("2"), specialisations))
    structure = get_program_structure(user['degree']['programCode'], specs=specialisations)[0]

    top_results = sorted(all_courses.items(), reverse=True,
                         key=lambda course: fuzzy_match(course, search_string)
                         )[:100]
    weighted_results = sorted(top_results, reverse=True,
                              key=lambda course: weight_course(course,
                                                               search_string,
                                                               structure,
                                                               majors,
                                                               minors)
                              )[:30]

    return dict(weighted_results)


@router.post(
    "/getAllUnlocked/",
    response_model=CoursesState,
    responses={
        400: {"description": "Uh oh you broke me"},
        200: {
            "description": "Returns the state of all the courses",
            "content": {
                "application/json": {
                    "example": {
                        "COMP9302": {
                            "is_accurate": True,
                            "unlocked": True,
                            "handbook_note": "This course can only be taken in the final term of your program.",
                            "warnings": [],
                        }
                    }
                }
            },
        },
    },
)
def get_all_unlocked(uid: Annotated[str, Security(require_uid)]) -> CoursesState:
    """
    Given the userData and a list of locked courses, returns the state of all
    the courses. Note that locked courses always return as True with no warnings
    since it doesn't make sense for us to tell the user they can't take a course
    that they have already completed
    """
    user = get_setup_user(uid)
    algo_user = user_storage_to_algo_user(user)
    courses_states = get_all_course_states_for_user(algo_user)
    return CoursesState(courses_state=courses_states)


@router.get(
    "/getLegacyCourses/{year}/{term}",
    response_model=ProgramCourses,
    responses={
        400: {"description": "Year or Term input is incorrect"},
        200: {
            "description": "Returns the program structure",
            "content": {
                "application/json": {
                    "example": {
                        "courses": {
                            "ACCT1511": "Accounting and Financial Management 1B",
                            "ACCT2542": "Corporate Financial Reporting and Analysis",
                            "ACCT3202": "Industry Placement 2",
                            "ACCT3303": "Industry Placement 3",
                            "ACCT3610": "Business Analysis and Valuation",
                            "ACCT4797": "Thesis (Accounting) B",
                            "ACCT4809": "Current Developments in Auditing Research",
                            "ACCT4852": "Current Developments in Accounting Research - Managerial",
                            "ACCT4897": "Seminar in Research Methodology",
                            "ACTL1101": "Introduction to Actuarial Studies",
                            "ACTL2101": "Industry Placement 1",
                            "ACTL2102": "Foundations of Actuarial Models",
                            "ACTL3142": "Actuarial Data and Analysis",
                        }
                    }
                }
            },
        },
    },
)
def get_legacy_courses(year, term) -> Dict[str, Dict[str, str]]:
    """
    Gets all the courses that were offered in that term for that year
    """
    result = {c['code']: c['title'] for c in archivesDB[year].find() if term in c['terms']}

    if not result:
        raise HTTPException(status_code=400, detail="Invalid term or year. Valid terms: T0, T1, T2, T3. Valid years: 2019, 2020, 2021, 2022.")

    return {'courses' : result}


@router.get("/getLegacyCourse/{year}/{courseCode}")
def get_legacy_course(year: str, courseCode: str):
    """
        Like /getCourse/ but for legacy courses in the given year.
        Returns information relating to the given course
    """
    result = get_legacy_course_details(courseCode, year)
    return result


@router.post("/unselectCourse/{unselectedCourse}", response_model=CourseCodes,
            responses={
                400: {"description": "Uh oh you broke me"},
                200: {
                    "description": "Returns the state of all the courses",
                    "content": {
                        "application/json": {
                            "example": {
                                 "courses": [
                                     "COMP1521",
                                     "COMP1531",
                                     "COMP3121"
                                 ]
                             }
                         }
                     }
                 }
            })
def unselect_course(uid: Annotated[str, Security(require_uid)], unselectedCourse: str) -> dict[str, list[str]]:
    """
    Creates a new user class and returns all the courses
    affected from the course that was unselected in alphabetically sorted order

    NOTE: No longer in use...
    """
    user_data = get_setup_user(uid)
    user = user_storage_to_algo_user(user_data)
    if not user.has_taken_course(unselectedCourse):
        return { 'courses' : [] }

    affected_courses = []
    # Brute force loop through all taken courses and if we find a course which is
    # no longer unlocked, we unselect it, add it to the affected course list,
    # then restart loop.
    courses_to_delete = [unselectedCourse]
    while courses_to_delete:
        affected_courses.extend(courses_to_delete)
        for course in courses_to_delete:
            if user.has_taken_course(course):
                user.pop_course(course)

        courses_to_delete = [
            c
            for c in user.get_courses()
            if CONDITIONS.get(c) is not None  # course is in conditions
            and not (CONDITIONS[c].validate(user))[0]  # not unlocked anymore
        ]

    return { 'courses' : list(sorted(affected_courses)) }


@router.get("/courseChildren/{course}", response_model=CoursesPath,
            responses = {
                200 : {
                    "courses": ["COMP1521", "COMP1531"]
                }
            })
def course_children(course: str):
    """
    fetches courses which are dependent on taking 'course'
    eg 1511 -> 1521, 1531, 2521 etc
    """
    if not CONDITIONS.get(course):
        raise HTTPException(400, f"no course by name {course}")
    return {
            "original" : course,
            "courses": [
                coursename for coursename, condition in CONDITIONS.items()
                if condition is not None and condition.is_path_to(course)
            ]
        }

@router.get("/getPathFrom/{course}", response_model=CoursesPath,
            responses = {
                200 : {
                    "courses": ["COMP1521", "COMP1531"]
                }
            })
def get_path_from(course: str) -> CoursesPathDict:
    """
    fetches courses which can be used to satisfy 'course'
    eg 2521 -> 1511
    """
    return {
        "original" : course,
        "courses" : get_incoming_edges(course),
    }

@router.post("/coursesUnlockedWhenTaken/{courseToBeTaken}", response_model=CoursesUnlockedWhenTaken,
            responses={
                400: { "description": "Uh oh you broke me" },
                200: {
                    "description": "Returns all courses which are unlocked when this course is taken",
                    "content": {
                        "application/json": {
                            "example": {
                                "direct_unlock": ["COMP2511", "COMP3311"],
                                "indirect_unlock": []
                            }
                        }
                    }
                }
            })
def courses_unlocked_when_taken(uid: Annotated[str, Security(require_uid)], courseToBeTaken: str) -> Dict[str, List[str]]:
    """ Returns all courses which are unlocked when given course is taken """
    user = get_setup_user(uid)
    algo_user = user_storage_to_algo_user(user)

    ## initial state
    courses_initially_unlocked = unlocked_set(get_all_course_states_for_user(algo_user))
    ## add course to the user
    algo_user.add_courses({ courseToBeTaken: (get_course_details(courseToBeTaken)['UOC'], None) })
    ## final state
    courses_now_unlocked = unlocked_set(get_all_course_states_for_user(algo_user))
    new_courses = courses_now_unlocked - courses_initially_unlocked

    ## Differentiate direct and indirect unlocks
    path_to = set(course_children(courseToBeTaken)["courses"])
    direct_unlock = new_courses.intersection(path_to)
    indirect_unlock = new_courses - direct_unlock

    return {
        'direct_unlock': sorted(list(direct_unlock)),
        'indirect_unlock': sorted(list(indirect_unlock))
    }


@router.get(
    "/termsOffered/{course}/{years}",
    response_model=TermsList,
    responses={
        400: {
            "description": "The given course code could not be found in the database",
        },
        200: {
            "description": "Returns the terms a course is offered in",
            "content": {
                "application/json": {
                    "example": {
                        "terms": {
                            "2022": [ "T1", "T2", "T3" ],
                        },
                        "fails": [
                            [
                                "COMP1511",
                                "2023",
                                {
                                    "status_code": 400,
                                    "detail": "invalid course code or year",
                                    "headers": None
                                }
                            ]
                        ]
                    },
                },
            },
        },
    }
)
def terms_offered(course: str, years:str) -> TermsOffered:
    """
    Recieves a course and a list of years. Returns a list of terms the
    course is offered in for the given years.

    Expected Input:
        course: (str) CODEXXXX
        years: (str): `+`-connected string of years
            eg: "2020+2021+2022"
    Output: {
            year: [terms offered],
            fails: [(year, exception)]
        }
    """
    offerings, fails = get_terms_offered_multiple_years(course, years.split("+"))

    return {
        "terms": offerings,
        "fails": fails,
    }


###############################################################################
#                                                                             #
#                             End of Routes                                   #
#                                                                             #
###############################################################################


def unlocked_set(courses_state: dict[str, CourseState]) -> Set[str]:
    """ Fetch the set of unlocked courses from the courses_state of a getAllUnlocked call """
    return set(course for course in courses_state if courses_state[course].unlocked)

def is_course_unlocked(course: str, user: User) -> Tuple[bool, List[str]]:
    """
    Returns if the course is unlocked for the given user.
    Also returns a list of warnings.
    TODO: !Untested
    """
    course_result, course_warnings = (
        cond.validate(user) if (cond := CONDITIONS[course]) else (True, [])
    )

    # TODO: remove this as blank once program_restrictions return warnings
    program_warnings: List[str] = []
    program_restriction = get_program_restriction(user.program) or NoRestriction()
    program_result = program_restriction.validate_course_allowed(user, course)

    return (course_result and program_result), (course_warnings + program_warnings)

def fuzzy_match(course: Tuple[str, str], search_term: str) -> float:
    """ Gives the course a weighting based on the relevance to the search """
    code, title = course

    # either match against a course code, or match many words against the title
    # (not necessarily in the same order as the title)
    search_term = search_term.lower()
    if re.match('[a-z]{4}[0-9]', search_term):
        return fuzz.ratio(code.lower(), search_term) * 10

    return max(fuzz.ratio(code.lower(), search_term),
               sum(fuzz.partial_ratio(title.lower(), word)
                       for word in search_term.split(' ')))

def weight_course(course: tuple[str, str], search_term: str, structure: dict, majors: list, minors: list) -> float:
    """ Gives the course a weighting based on the relevance to the user's degree """
    weight = fuzzy_match(course, search_term)
    code, _ = course

    # TODO: could this function be refactored to generate a mapping of all codes to their weight deltas for a given structure,
    #       and then we wouldn't need to run this on every course code?
    # pylint: disable-next=too-many-nested-blocks  # TODO: refactor
    for structKey in structure.keys():
        if "Major" not in structKey:
            continue
        for key in structure[structKey].items():
            if isinstance(key[1], dict):
                for c in key[1].get("courses", {}):
                    if code in c:
                        if re.match("core|prescribed", key[0], flags=re.IGNORECASE):
                            weight += 40
                        else:
                            weight += 20
                        break

    for major_code in majors:
        if str(code).startswith(major_code[:4]):
            weight += 14
            break

    # pylint: disable-next=too-many-nested-blocks  # TODO: refactor
    for structKey in structure.keys():
        if "Minor" not in structKey:
            continue
        for key in structure[structKey].items():
            if isinstance(key[1], dict):
                for c in key[1].get("courses", {}):
                    if code in c:
                        if re.match("core|prescribed", key[0], flags=re.IGNORECASE):
                            weight += 20
                        else:
                            weight += 10
                        break

    for minor_code in minors:
        if str(code).startswith(minor_code[:4]):
            weight += 7
            break

    return weight

def get_program_restriction(program_code: Optional[str]) -> Optional[ProgramRestriction]:
    """
    Returns the program restriction for the given program code.
    Also responsible for starting up `PROGRAM_RESTRICTIONS` the first time it is called.
    !Untested
    """
    # TODO: This loading should not be here; very slow
    # making it global causes some errors
    # There needs to be a startup event for routers to load data
    # TODO-OLLI(pm): ^ we now have a global startup event, we can setup and cache pickle data there
    if not program_code:
        return None
    with open(PROGRAM_RESTRICTIONS_PICKLE_FILE, "rb") as file:
        program_restrictions: dict[str, ProgramRestriction] = pickle.load(file)
    return program_restrictions.get(program_code, None)
