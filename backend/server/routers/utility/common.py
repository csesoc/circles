"""
General purpose utility functions for the server, that do not fit
specifically in any one function
"""

from contextlib import suppress
import functools
import re
from typing import Callable, Mapping, Optional, Tuple, TypeVar, cast

from fastapi import HTTPException

from algorithms.objects.course import Course
from data.processors.models import CourseContainer, Program, ProgramContainer, SpecData, Specialisation, SpecsData
from data.config import ARCHIVED_YEARS, GRAPH_CACHE_FILE, LIVE_YEAR
from data.utility import data_helpers
from server.routers.utility.manual_fixes import apply_manual_fixes
from server.routers.model import CONDITIONS, CoursesPathDict, ProgramTime, StructureContainer
from server.db.mongo.conn import archivesDB, coursesCOL, programsCOL, specialisationsCOL

# TODO: move these constants out into new file, or move model.py ones into here (once we dont have top-level connection initialisation)
COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")
GRAPH: dict[str, dict[str, list[str]]] = data_helpers.read_data(GRAPH_CACHE_FILE)
INCOMING_ADJACENCY: dict[str, list[str]] = GRAPH.get("incoming_adjacency_list", {})

# P = ParamSpec('P')  # TODO: type the args and kwargs here using ParamSpec, pylint cries rn
R = TypeVar('R')  # TODO: might be able to inline this https://typing.readthedocs.io/en/latest/spec/generics.html#variance-inference
def map_suppressed_errors(func: Callable[..., R], errors_log: list[tuple], *args, **kwargs) -> Optional[R]:
    """
    Map a function to a list of arguments, and return the result of the function
    if no error is raised. If an error is raised, log the error and return None.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        errors_log.append((*args, str(e)))
    return None


def get_core_courses(program: str, specialisations: list[str]):
    structure = get_program_structure(program, specs=specialisations)[0]
    return sum((
                sum((
                    list(value["courses"].keys())
                    for sub_group, value in spec["content"].items()
                    if 'core' in sub_group.lower()
                ), [])
                for spec_name, spec in structure.items()
                if "Major" in spec_name or "Honours" in spec_name)
         , [])


def get_course_object(code: str, prog_time: ProgramTime, locked_offering: Optional[tuple[int, int]] = None, mark: Optional[int] = 100) -> Course:
    '''
    This return the Course object for the given course code.
    Note the difference between this and the get_course_details function
    '''
    if mark is None:
        mark = 100

    years = [str(year) for year in range(prog_time.startTime[0], prog_time.endTime[0] + 1)]
    terms_result = get_terms_offered_multiple_years(code, years)[0]
    terms_possible = {
        int(year): [int(term[1]) for term in terms]
        for year, terms in terms_result.items()
    }

    try:
        return Course(
            code,
            CONDITIONS[code],
            mark,
            COURSES[code]["UOC"],
            terms_possible,
            locked_offering
        )
    except KeyError as err:
        raise KeyError(f"Course {code} not found (course is most likely discontinued)") from err

def get_course_details(code: str) -> dict:  # TODO: type this output
    '''
    Get info about a course given its courseCode
    - start with the current database
    - if not found, check the archives

    Raises if not found
    '''
    # TODO: make take in a year, and be explicit about getting archived or not

    result = coursesCOL.find_one({"code": code})
    if not result:
        for year in sorted(ARCHIVED_YEARS, reverse=True):
            result = archivesDB[str(year)].find_one({"code": code})
            if result is not None:
                result["is_legacy"] = True  # TODO: is_legacy might not actually mean what it is used for here
                break
    else:
        result["is_legacy"] = False

    # if not result:
    #     return None
    if not result:
        raise HTTPException(
            status_code=400, detail=f"Course code {code} was not found"
        )

    result.setdefault("school", None)
    result.setdefault("raw_requirements", "")

    with suppress(KeyError):
        del result["exclusions"]["leftover_plaintext"]
    del result["_id"]

    return result

# TODO: make all of these year params ints
def get_legacy_course_details(code: str, year: str) -> dict:  # TODO: type output
    '''
    Returns the course details for a legacy year, similarly to get_course_details.

    Will raise a 400 if the course code could not be found in that year.
    '''
    result = archivesDB.get_collection(year).find_one({"code": code})
    if not result:
        raise HTTPException(status_code=400, detail="invalid course code or year")

    del result["_id"]
    result["is_legacy"] = False # not a legacy, assuming you know what you are doing

    return result

def get_terms_offered(code: str, year: str) -> list[str]:
    '''
    Returns the terms in which the given course is offered, for the given year.
    If the year is from the future then, backfill the LIVE_YEAR's results
    '''
    course_info = get_course_details(code) if int(year) >= LIVE_YEAR else get_legacy_course_details(code, year)
    return course_info['terms'] or []

def get_terms_offered_multiple_years(code: str, years: list[str]) -> Tuple[dict[str, list[str]], list[tuple]]:
    '''
    Returns the term offerings for a course code over multiple years, or an empty list if it could not be found.
    Also returns the years that were not found, and their specific errors.
    '''
    fails: list[tuple] = []
    offerings: dict[str, list[str]] = {
        year: map_suppressed_errors(get_terms_offered, fails, code, year) or []
        for year in years
    }

    return offerings, fails

def get_all_specialisations(program_code: str) -> Optional[SpecsData]:
    '''
    Returns the specs for the given programCode, removing any specs that are not supported.
    '''
    program = cast(Optional[Program], programsCOL.find_one({"code": program_code}))
    if program is None:
        return None

    # TODO: this can be done in a single aggregate
    raw_specs = program["components"].get("spec_data")
    if raw_specs is None:
        return {}
    for spec_type_container in raw_specs.values():
        spec_type_container = cast(dict[str, SpecData], spec_type_container)
        for program_specs in spec_type_container.values():
            for code in [*program_specs["specs"].keys()]:
                if not specialisationsCOL.find_one({"code": code}):
                    del program_specs["specs"][code]

    return raw_specs

def get_program_structure(program_code: str, specs: Optional[list[str]] = None, ignored: Optional[list[str]] = None) -> Tuple[dict[str, StructureContainer], int]:
    """Gets the structure of a course given specs and program code, ignoring what is specified."""
    # TODO: This ugly, use compose instead
    if ignored is None:
        ignored = []

    structure: dict[str, StructureContainer] = {}
    uoc = 0 # ensure always atleast set regardless of ignore  # TODO: None?
    if "spec" not in ignored and specs is not None:
        structure = add_specialisations_to_structure(structure, specs)
    if "code_details" not in ignored:
        structure, uoc = add_program_code_details_to_structure(structure, program_code)
    if "gened" not in ignored:
        structure = add_geneds_to_structure(structure, program_code)
    apply_manual_fixes(structure, program_code)

    return structure, uoc

def add_specialisation_to_structure(structure: dict[str, StructureContainer], code: str) -> None:
    """ Add a specialisation to the structure of a getStructure call """
    # in a specialisation, the first container takes priority - no duplicates may exist
    if code.endswith("1"):
        type = "Major"
    elif code.endswith("2"):
        type = "Minor"
    else:
        type = "Honours"

    spnResult = cast(Optional[Specialisation], specialisationsCOL.find_one({"code": code}))
    type = f"{type} - {code}"
    if not spnResult:
        raise HTTPException(status_code=400, detail=f"{code} of type {type} not found")

    structure[type] = {"name": spnResult["name"], "content": {}}
    # NOTE: takes Core Courses are first
    exceptions: list[str] = []
    for cores in filter(lambda a: "Core" in a["title"], spnResult["curriculum"]):
        new = add_subgroup_container_to_structure(structure, type, cores, exceptions)
        exceptions.extend(new)

    for container in spnResult["curriculum"]:
        if "Core" not in container["title"]:
            add_subgroup_container_to_structure(structure, type, container, exceptions)

def add_specialisations_to_structure(structure: dict[str, StructureContainer], specs: list[str]) -> dict[str, StructureContainer]:
    """
        Take a list of specs and adds them to the structure
    """
    for m in specs:
        add_specialisation_to_structure(structure, m)
    return structure

def add_program_code_details_to_structure(structure: dict[str, StructureContainer], program_code: str) -> Tuple[dict[str, StructureContainer], int]:
    """
    Add the details for given program code to the structure.
    Returns:
        - structure
        - uoc (int) associated with the program code.
    """
    programsResult = cast(Optional[Program], programsCOL.find_one({"code": program_code}))
    if not programsResult:
        raise HTTPException(status_code=400, detail="Program code was not found")

    structure['General'] = {"name": "General Program Requirements", "content": {}}
    structure['Rules'] = {"name": "General Program Rules", "content": {}}
    return (structure, programsResult["UOC"])

def add_subgroup_container_to_structure(structure: dict[str, StructureContainer], type: str, container: ProgramContainer | CourseContainer, exceptions: list[str]) -> list[str]:
    """ Returns the added courses """
    # TODO: further standardise non_spec_data to remove these lines:

    title = container.get("title", "")
    if container.get("type") == "gened":
        title = "General Education"
    conditional_type = container.get("type")
    if conditional_type is not None and "rule" in conditional_type:
        type = "Rules"
    structure[type]["content"][title] = {
        "UOC": container.get("credits_to_complete") or 0,
        "courses": functools.reduce(
            lambda rest, current: rest | {
                course: description for course, description
                in convert_subgroup_object_to_courses_dict(current[0], current[1]).items()
                if course not in exceptions
            }, container.get("courses", {}).items(), {}
        ),
        "type": container.get("type", ""),
        "notes": container.get("notes", "") if type == "Rules" else ""
    }
    return list(structure[type]["content"][title]["courses"].keys())

def get_gen_eds(
        programCode: str, excluded_courses: Optional[list[str]] = None
    ) -> dict[str, dict[str, str]]:
    """
    fetches gen eds from file and removes excluded courses.
        - `programCode` is the program code to fetch geneds for
        - `excluded_courses` is a list of courses to exclude from the gened list.
        Typically the result of a `courseList` from `getStructure` to prevent
        duplicate courses between cores, electives and geneds.
    """
    excluded_courses = excluded_courses if excluded_courses is not None else []
    try:
        geneds: dict[str, str] = data_helpers.read_data("data/scrapers/genedPureRaw.json")[programCode]
    except KeyError as err:
        raise HTTPException(status_code=400, detail=f"No geneds for progrm code {programCode}") from err

    for course in excluded_courses:
        if course in geneds:
            del geneds[course]

    return {"courses": geneds}

def add_geneds_courses_to_structure(programCode: str, structure: dict[str, StructureContainer], container: ProgramContainer) -> list[str]:
    """ Returns the added courses """
    if container.get("type") != "gened":
        return []

    item = structure["General"]["content"]["General Education"]
    item["courses"] = {}
    if container.get("courses") is None:
        gen_ed_courses = list(set(get_gen_eds(programCode)["courses"].keys()) - set(sum(
            (
                sum((
                    list(value["courses"].keys())
                    for sub_group, value in spec["content"].items()
                    if 'core' in sub_group.lower()
                ), [])
            for spec_name, spec in structure.items()
            if "Major" in spec_name or "Honours" in spec_name)
        , [])))
        geneds = get_gen_eds(programCode)
        item["courses"] = {course: geneds["courses"][course] for course in gen_ed_courses}


    return list(item["courses"].keys())

# TODO: This should be computed at scrape-time
def add_geneds_to_structure(structure: dict[str, StructureContainer], programCode: str) -> dict[str, StructureContainer]:
    """
        Insert geneds of the given programCode into the structure
        provided
    """
    programsResult = cast(Optional[Program], programsCOL.find_one({"code": programCode}))
    if programsResult is None:
        raise HTTPException(
            status_code=400, detail="Program code was not found")

    with suppress(KeyError):
        for container in programsResult['components']['non_spec_data']:
            add_subgroup_container_to_structure(structure, "General", container, [])
            if container.get("type") == "gened":
                add_geneds_courses_to_structure(programCode, structure, container)
    return structure

def convert_subgroup_object_to_courses_dict(object: str, description: str | list[str]) -> Mapping[str, str | list[str]]:
    """ Gets a subgroup object (format laid out in the processor) and fetches the exact courses its referring to """

    if " or " in object and isinstance(description, list):
        return {c: description[index] for index, c in enumerate(object.split(" or "))}
    if not re.match(r"[A-Z]{4}[0-9]{4}", object):
        return regex_search(rf"^{object}")

    return { object: description }

def regex_search(search_string: str) -> Mapping[str, str]:
    """
    Uses the search string as a regex to match all courses with an exact pattern.
    """

    pat = re.compile(search_string, re.I)
    courses = list(coursesCOL.find({"code": {"$regex": pat}}))

    # TODO: do we want to always include matching legacy courses (excluding duplicates)?
    if not courses:
        for year in sorted(ARCHIVED_YEARS, reverse=True):
            courses = list(archivesDB[str(year)].find({"code": {"$regex": pat}}))
            if courses:
                break

    return {course["code"]: course["title"] for course in courses}

def get_incoming_edges(course_code: str) -> list[str]:
    """
    returns the course codes that can be used to satisfy 'course', eg 2521 -> 1511.

    (previously from `get_path_from`)
    """
    return INCOMING_ADJACENCY.get(course_code, [])

def convert_adj_list_to_edge_list(proto_edges: list[CoursesPathDict]) -> list[dict[str, str]]:
    """
    Take the proto-edges created by calls to `path_from` and convert them into
    a full list of edges of form.
    [
        {
            "source": (str) - course_code,  # This is the 'original' value
            "target": (str) - course_code,  # This is the value of 'courses'
        }
    ]
    Effectively, turning an adjacency list into a flat list of edges.

    (previously `proto_edges_to_edges`)
    """
    edges = []
    for proto_edge in proto_edges:
        # Incoming: { original: str,  courses: list[str]}
        # Outcome:  { "src": str, "target": str }
        if not proto_edge["courses"]:
            continue
        for course in proto_edge["courses"]:
            edges.append({
                    "source": course,
                    "target": proto_edge["original"],
                }
            )
    return edges

def prune_edges(edges: list[dict[str, str]], courses: list[str]) -> list[dict[str, str]]:
    """
    Remove edges between vertices that are not in the list of courses provided.
    """
    return [edge for edge in edges if edge["source"] in courses and edge["target"] in courses]
