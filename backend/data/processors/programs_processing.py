"""
Program processes the formatted data by editing and customising the data for
use on the frontend. See 'programsProcessed.json' for output.

Status: Currently works for all COMP programs and SENGAH. Query next
        set of programs to include.

Step in the data's journey:
    [   ] Scrape raw data (program_scraper.py)
    [   ] Format scraped data (program_formatting.py)
    [ X ] Customise formatted data (program_processing.py)
"""
# pylint: disable=too-many-function-args

import re
from collections import OrderedDict
from typing import Optional

from data.utility.data_helpers import read_data, write_data

# Data input/output paths
INPUT_PATH = "data/scrapers/programsFormattedRaw.json"
OUTPUT_PATH = "data/final_data/programsProcessed.json"
FACULTY_CODE_PATH = "data/final_data/facultyCodesProcessed.json"

# Keys for each item in the data
SPEC_KEY = "spec_data"
NON_SPEC_KEY = f"non_{SPEC_KEY}"

# List of all program codes that include a computer science degree
CS_PROGS = (
    "3673",  # NOTE: Ecomonics major is optional, no general education, program constraints(?), UNSW Business Electives
    "3674",
    "3778",
    "3779",
    "3781",
    "3782",
    "3783",
    "3784",
    "3785",
    "3786",
    "3789",
    "3791",
    "4515",
    "7003",
    "7022"
)

# List of all program codes that include an engineering degree
ENG_PROGS = (
    "3131",
    "3132",
    "3133",
    "3134",
    "3707",
    "3736",
    "3761",
    "3762",
    "3764",
    "3765",
    "3766",
    "3767",
    "3768",
    "3769",
    "3773",
    "3776",
    "3785",
    "3961",
    "4471",
    "4472",
    "4473",
    "4474",
    "4475",
    "4476",
    "4477",
    "4478",
    "4515"
)

OTH_PROGS = (
    "3502",
    "3053",
    "3979",
    "3959",
    "3181",
    "3543",
    "3586",
    "3805",
    "3871",
    "3956",
    "3454",
    "3453",
    "3970",
    "3707",
    "3543",
)

# Enable or disable testing, and choose what programs to test on
TESTING_MODE = False
TEST_PROGS = CS_PROGS + OTH_PROGS

def process_prg_data() -> None:
    """
    Read in INPUT_PATH, process them and write to OUTPUT_PATH
    """
    data = read_data(INPUT_PATH)
    single_degrees = [ val for val in data.values() if "/" not in val["title"] ]
    double_degrees = [ val for val in data.values() if "/" in val["title"] ]

    # Process single degrees then double degrees
    processed_data: dict[str, dict] = {}
    for formatted_data in single_degrees:
        add_program(processed_data, formatted_data)
    for formatted_data in double_degrees:
        add_program(processed_data, formatted_data)

    processed_data = order_dict_alphabetically(processed_data)
    write_data(processed_data, OUTPUT_PATH)


def add_program(processed_data: dict[str, dict], formatted_data: dict):
    """
    Adds program to processed_data if it's not in testing mode
    OR if we're in testing mode and it's in the testing list
    """
    # Get program specific data
    if not TESTING_MODE or formatted_data["code"] in TEST_PROGS:
        program_data = initialise_program(formatted_data)

        # Loop through items in curriculum structure and add to the program data
        for item in formatted_data["structure"]:
            add_component_data(processed_data, program_data, item)

        # Order dict alphabetically
        program_data["components"] = order_dict_alphabetically(program_data["components"])
        if SPEC_KEY in program_data["components"]:
            program_data["components"][SPEC_KEY] = order_dict_alphabetically(program_data["components"][SPEC_KEY])

        code = program_data["code"]
        processed_data[code] = program_data


def order_dict_alphabetically(dict: dict) -> OrderedDict:
    """
    Takes in dictionary and returns ordered dictionary sorted
    alphabetically by the 'key' strings
    """
    return OrderedDict(sorted(dict.items(), key=lambda t: t[0]))


def initialise_program(program: dict) -> dict:
    """
    Initialises basic attributes of the specialisation.
    """
    duration = re.search(r"(\d)", program["duration"])
    assert duration is not None
    duration_var = duration.group(1)

    return {
        "title": program["title"],
        "code": program["code"],
        "duration": int(duration_var),
        "UOC": int(program["UOC"]),
        "faculty": program["faculty"],
        "overview": program["overview"],
        "structure_summary": program["structure_summary"],
        "components": {},
        "processing_warnings": [],
    }


def add_component_data(processed_data: dict[str, dict], program_data: dict, item: dict, program_name = None, is_optional = False) -> None:
    """
    Adds data within a given item to a given program recursively
    """
    if any(
        key not in item
        for key in ("vertical_grouping", "title")
    ):
        return

    is_optional = is_optional or is_substring("optional", item["description"])

    program_name = find_program_name(program_data, item) if program_name is None else program_name

    # Figure out what type of requirement we're looking at,
    # and add it to the appropriate spot in the program data
    if is_general_education(item):
        add_general_education_data(program_data, item)
    if is_specialisation(item):
        add_specialisation_data(processed_data, program_data, item, program_name, is_optional)
    if is_core_course(item):
        add_course_data(program_data, item, "core_courses")
        return
    if is_information_rule(item):
        add_information_rule(program_data, item)
    if is_limit_rule(item):
        add_limit_rule(program_data, item)
    if is_prescribed_elective(item):
        add_course_data(program_data, item, "prescribed_electives")
        return
    if is_other(item):
        add_course_data(program_data, item, "other")
        return

    # Recurse further down through the container and the relationship list
    for next in item["relationship"]:
        add_component_data(processed_data, program_data, next, program_name = program_name, is_optional = is_optional)
    for next in item["container"]:
        add_component_data(processed_data, program_data, next, program_name = program_name, is_optional = is_optional)


def split_program_names(title: str) -> list[str]:
    """
    Splits the title into it's single degrees and gets rid of white space
    """
    program_names = title.split("/")
    return list(map(lambda s: s.strip(), program_names))


def find_program_name(program_data: dict, item: dict) -> Optional[str] :
    """
    Find the program name (if possible).
    Returns a string with the program name if found,
    else returns None
    """
    program_names = split_program_names(program_data["title"])

    # Check if we even need to bother searching
    if len(program_names) == 1:
        return program_names[0]

    # Sort by longest length first
    program_names = sorted(program_names, key = lambda s: -len(s))

    # Print a warning if one of the strings is a substring of the other
    if is_substring(program_names[0], program_names[1]):
        add_warning(f"{program_names[0]} is a substring of {program_names[1]}", program_data, item)
    if is_substring(program_names[1], program_names[0]):
        add_warning(f"{program_names[1]} is a substring of {program_names[0]}", program_data, item)

    # Search
    for program_name in program_names:
        if program_name in item["title"]:
            return program_name
        for container in item["container"]:
            if program_name in container["title"]:
                return program_name
    return None

def is_substring(needle: str, haystack: str) -> bool:
    """
    Returns boolean whether needle is a substring of haystack
    (case insensitive)
    """
    needle_escaped = re.escape(needle)
    return bool(re.match(needle_escaped, haystack, flags = re.IGNORECASE))


def is_general_education(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a general education requirement
    """
    return item["vertical_grouping"]["value"] == "GE"


def is_specialisation(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a specialisation requirement
    """
    return item["vertical_grouping"]["value"] in (
        "undergrad_major",
        "undergrad_minor",
        "honours",
        "any_spec"
    )


def is_core_course(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a core course requirement
    """
    return item["vertical_grouping"]["value"] == "CC"


def is_information_rule(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is an information rule
    """
    return item["vertical_grouping"]["value"] == "IR"


def is_limit_rule(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a limit rule
    """
    return item["vertical_grouping"]["value"] == "LR"


def is_prescribed_elective(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a prescribed elective
    """
    return item["vertical_grouping"]["value"] == "PE"


def is_other(item: dict) -> bool:
    """
    Returns boolean depending on if the given container is a 'other'
    """
    return not re.match("Free Elective", item["title"], flags=re.IGNORECASE)  and item["vertical_grouping"]["value"] == "FE"


def add_general_education_data(program_data: dict, item: dict) -> None:
    """
    Adds general education data to the correct spot in program_data
    """
    # Double check we haven't somehow already added the general education stuff already
    program_data["components"].setdefault(NON_SPEC_KEY, [])
    if any(req["type"] == "gened" for req in program_data["components"][NON_SPEC_KEY]):
        add_warning("Already added general education", program_data, item)

    program_data["components"][NON_SPEC_KEY].append({
        "type": "gened",
        "credits_to_complete": get_container_credits(program_data, item),  # TODO: Fix this
        "notes": item["description"],
    })


def contains_spec(components: dict[str, dict], new_spec: dict, spec_type_key: str) -> bool:
    """
    Returns boolean based on whether spec_data
    contains new_spec under spec_type_key
    """
    # Check if there actually is a spec_type_key field
    if SPEC_KEY not in components or spec_type_key not in components[SPEC_KEY]:
        return False

    # Check if this is indeed a single degree (that has specialisations)
    degrees = components[SPEC_KEY][spec_type_key].values()
    if len(degrees) != 1:
        return False

    # Finally, check if this spec is same as the new spec
    spec = list(degrees)[0]
    return spec == new_spec


def add_specialisation_data(processed_data: dict, program_data: dict, item: dict, program_name: str, is_optional: bool) -> None:
    """
    Adds specialisation data to the correct spot in program_data given a field and name of program
    """
    for spec_type in ("major", "minor", "honours"):
        # pylint: disable=cell-var-from-loop
        # Filter out all items that aren't spec_type
        spec_type_items = list(filter(
            lambda r: r["academic_item_type"] is not None and r["academic_item_type"]["value"] == spec_type,
            item["relationship"]
        ))

        # Found nothing...
        if not spec_type_items:
            continue

        new_data = {
            "is_optional": spec_type == "minor" or is_optional,
            "specs": {},
            "notes": item["description"],
        }
        for specialisation in spec_type_items:
            code = specialisation["academic_item_code"]
            if code is not None:
                new_data["specs"][code] = specialisation["academic_item_name"]

        # Figure out if it's optional
        spec_type_key = spec_type if spec_type[-1] == "s" else f"{spec_type}s"

        # If we don't have a program name yet, try to find one
        if program_name is None:
            # We know this is a double degree
            single_degrees = [
                val["title"] for val in processed_data.values()
                if "/" not in val["title"] and contains_spec(val["components"], new_data, spec_type_key)
            ]

            if len(single_degrees) != 1:
                # Didn't find program name :(
                add_warning("Couldn't find any of the program names for double degree", program_data, item)
            else:
                program_name = single_degrees[0]

        # Add this specialisation (if it doesn't exist)
        program_data["components"].setdefault(SPEC_KEY, {})
        spec_data = program_data["components"][SPEC_KEY]
        spec_data.setdefault(spec_type_key, {})

        # Check if there was already a <spec_type_key> added
        if program_name in spec_data[spec_type_key]:
            # Merge this entry and the previous one. Also add a warning
            curr_data = spec_data[spec_type_key][program_name]
            curr_data["specs"] = curr_data["specs"] | new_data["specs"]
            curr_data["notes"] = f"{curr_data['notes']}\n\n{new_data['notes']}"
            add_warning(f"There were two instances of {spec_type_key} for section {program_name}", program_data, item)
        else:
            # This is the only entry
            spec_data[spec_type_key].update({program_name: new_data})


def compute_levels(courses: dict[str, str]) -> list[int]:
    """
    From a dictionary of courses, figures out a list of ints
    of all levels present. If any course is wildcarded,
    then a list of numbers 1-9 is returned
    """
    # If any of the courses are less than 5 chars (ie they're just a number)
    # then assume it's any level. Additionally, if the 5th char is wildcarded
    # (with a '.'), assume it's any level
    codes = []
    for key in courses.keys():
        codes += key.split(" or ")

    if any(
        len(code) < 5 or code[4] == "."
        for code in codes
    ):
        return list(range(1, 10))

    # For some program structures `courses` may actually contain specialisations
    # such as Commerce International (3558).
    # Everything has a number (that isn't wildcarded).
    # Get all levels as a set to remove duplicates
    return list({int(code[4]) for code in courses.keys() if code[4].isdecimal()})


def add_course_data(program_data: dict, item: dict, req_type: str) -> None:
    """
    Adds core course data to the correct spot in program_data
    """
    courses: dict[str, str] = {}
    add_course_tabs(program_data, courses, item)

    program_data["components"].setdefault(NON_SPEC_KEY, [])
    program_data["components"][NON_SPEC_KEY].append({
        "type": req_type,
        "courses": order_dict_alphabetically(courses),
        "title": item["title"],
        "credits_to_complete": get_container_credits(program_data, item),  # TODO: fix this
        "levels": compute_levels(courses),
        "notes": item["description"],
    })


def add_information_rule(program_data: dict, item: dict) -> None:
    """
    Adds information rule data to the correct spot in program_data
    """
    program_data["components"].setdefault(NON_SPEC_KEY, [])
    program_data["components"][NON_SPEC_KEY].append({
        "type": "info_rule",
        "title": item["title"],
        "notes": item["description"],
    })


def add_limit_rule(program_data: dict, item: dict) -> None:
    """
    Adds limit rule data to the correct spot in program_data
    """
    # Split into description and requirements component
    description_lines = item["description"].split("\n")
    if len(description_lines) != 2:
        add_warning("Expected 1 newline for limit rule", program_data, item)
        return

    notes = description_lines[0]
    requirements_str = description_lines[1]

    # Process the limit rule descriptions to get credits and requirements
    credits_to_complete = get_string_credits(program_data, item, notes)  # TODO: fix this
    requirements = format_course_strings(requirements_str)

    courses: dict[str, str] = {}
    for requirement in requirements:
        process_any_requirement(program_data, courses, requirement, item)

    program_data["components"].setdefault(NON_SPEC_KEY, [])
    program_data["components"][NON_SPEC_KEY].append({
        "type": "limit_rule",
        "courses": order_dict_alphabetically(courses),
        "title": item["title"],
        "credits_to_complete": credits_to_complete,
        "levels": compute_levels(courses),
        "notes": notes,
    })


def add_course_tabs(program_data: dict, courses: dict, item: dict) -> None:
    """
    (Recursively) adds an entire drop down tab of courses requirements
    """
    if item["dynamic_relationship"]:
        for course in item["dynamic_relationship"]:
            process_any_requirement(program_data, courses, course["description"], item)
    elif item["vertical_grouping"]["value"] == "one_of_the_following":
        # Check if it's a 'one of the following' requirement or single course requirements
        combined_key = " or ".join([ course["academic_item_code"] for course in item["relationship"] ])
        courses[combined_key] = [ course["academic_item_name"] for course in item["relationship"] ]
    else:
        for course in item["relationship"]:
            # Check if it's just a normal course
            if course["academic_item_code"] is not None:
                # Normal course, add it
                code = course["academic_item_code"]
                courses[code] = course["academic_item_name"]
            elif course["parent_record"] != "Curriculum Structure Container: Free Electives":
                process_any_requirement(program_data, courses, course["parent_record"], item)

    # Recurse further down in case we've missed something
    for next in item["container"]:
        add_course_tabs(program_data, courses, next)


def process_any_requirement(program_data: dict, courses: dict, requirement: str, item: dict) -> None:
    """
    Processes list of course (as strings) requirements
    that are of the form 'any <faculty or type of course> course'
    """
    if bool(re.match(r"^any course$", requirement, flags = re.IGNORECASE)):
        # Manual fix
        codes = [""]
    # TODO: Why does this regex not work?!?!
    # elif bool(re.match(r"any course matching the pattern [A-Z]{4}[0-9#]{4}", requirement, re.IGNORECASE)):
    elif "any course matching the pattern " in requirement:
        # It's of the form 'any course matching the pattern ########'
        codes = [requirement[-8:].rstrip("#")]
        requirement = requirement[-40:]
    else:
        # Standard case
        stripped = strip_any_requirement_description(requirement)
        level = get_any_requirement_level(stripped)

        try:
            codes = get_any_requirement_codes(stripped, level)
        except ValueError as e:
            add_warning(e, program_data, item)
            return

    for code in codes:
        courses[code] = requirement


def format_course_strings(requirements_str: str) -> list[str]:
    """
    Format limit rule requirement string to match other rules format
    by making it into a list of strings of the form 'any <faculty> course'
    """
    # Get rid of useless keywords, codes and double spaces
    requirements_str = re.sub(r"(course|offered by|\([A-Z]{4}\))", " ", requirements_str, flags = re.IGNORECASE)
    requirements_str = re.sub(r"\s+", " ", requirements_str, flags = re.IGNORECASE)

    # Split into different requirements
    courses = re.split(r"\s*any\s*", requirements_str, flags = re.IGNORECASE)

    # Format
    courses = list(map(lambda s: s.strip(), courses))
    courses = list(filter(lambda s: s != "", courses))
    courses = list(map(lambda s: f"any {s} course", courses))

    return courses


def strip_any_requirement_description(requirement: str) -> str:
    """
    Get only the useful bit of any requirements.
    I.e., if requirement is of the form 'any <faculty> course'
    or 'any course offered by <faculty>' then get '<faculty>'
    """
    search_result = re.search(r"any (.+) course", requirement, flags = re.IGNORECASE)
    if search_result is None:
        search_result = re.search(r"any course offered by (.+)", requirement, flags = re.IGNORECASE)
    return search_result.group(1) if search_result else ""


def get_any_requirement_level(requirement: str) -> str:
    """
    Finds the level requirement (if there is any).
    If there isn't, returns empty string
    """
    search_result = re.search(r"level (\d)", requirement, flags = re.IGNORECASE)
    if search_result is not None:
        return search_result.group(1)
    return ""


def get_any_requirement_codes(stripped: str, level: str) -> list[str]:
    """
    Generates code from stripped requirement and level.
    Raises a ValueError if the faculty isn't in facultyCodesProcessed.json
    """
    # Find the faculty (if there is any)
    search_result = re.search(r"([a-zA-Z]\D+)$", stripped, flags = re.IGNORECASE)
    if search_result is None:
        # There is no faculty, return generic code
        return [f"....{level}"]

    # There is a faculty/school.
    # Format the faculty properly and get the mappings from faculties -> codes
    faculty = faculty_manual_fixes(search_result.group(1))
    mappings = read_data(FACULTY_CODE_PATH)

    try:
        faculty_codes = mappings[faculty]
    except KeyError as err:
        raise ValueError(f"Can't figure out what abbreviated code(s) are for {faculty}") from err

    return list(map(lambda c: f"{c}{level}", faculty_codes))


def faculty_manual_fixes(faculty: str) -> str:
    """
    Manual fixes to format keys into the
    form seen in facultyCodesProcessed.json
    """
    faculty = faculty.replace("School of", "S")
    faculty = faculty.replace("Faculty of", "F")

    # Manual fixes
    faculty = faculty.replace("S Medical Sciences", "S Medical")
    faculty = faculty.replace("F Medicine and Health", "F Medicine")
    # TODO: More manual fixes, but not sure what these are meant to become
    # General Education - F Business -> ????
    # Arts and Social Sciences -> ????
    return faculty


def get_credits_decorator(func):
    """
    Decorates the 'get credits' functions with some error
    checking and adds warning if needed
    """
    def wrapper(program_data: dict, item: dict, *args, **kwargs) -> int:
        try:
            return func(item, *args, **kwargs)
        except ValueError as e:
            add_warning(e, program_data, item)
            return 0
    return wrapper

@get_credits_decorator
def get_container_credits(item: dict) -> int:
    """
    Get the number of credits in this requirement.
    If there are no attached credits, returns 0
    """
    try:
        return int(item["credit_points"])
    except ValueError:
        pass

    try:
        return int(item["credit_points_max"])
    except ValueError as exec:
        raise ValueError("Couldn't find the number of credits for item") from exec


@get_credits_decorator
def get_string_credits(_: dict, notes: str) -> int:
    """
    Search for UOC conditions in the notes section of a limit rule
    """
    search_result = re.search(r"(\d+) *UOC", notes, flags = re.IGNORECASE)
    if search_result is not None:
        return int(search_result.group(1))
    raise ValueError("Couldn't find the number of credits for item")


def add_warning(w: Exception | str, program_data: dict, item: dict) -> None:
    """
    Adds warning in the form of either a string or Exception to a specific program/section
    """
    warning = f"{w} in program {program_data['title']} ({program_data['code']}) in section titled '{item['title']}'"
    program_data["processing_warnings"].append(warning)


if __name__ == "__main__":
    process_prg_data()
