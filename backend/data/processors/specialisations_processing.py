"""
Program processes the formatted data by editing and customising the data for
use on the frontend. See 'specialisationsProcessed.json' for output.

NOTE: "spn" == "specialisation"

Status: Currently works for all COMP specialisations and SENGAH. May need
        manual fixes for the "notes" fields (if they are to appear as
        text pop-ups).

Step in the data's journey:
    [   ] Scrape raw data (specialisationScraper.py)
    [   ] Format scraped data (specialisationFormatting.py)
    [ X ] Customise formatted data (specialisationProcessing.py)
"""

import re

from data.processors.programs_processing import TEST_PROGS
from data.utility.data_helpers import read_data, write_data

# TODO: add more specialisations as we expand scope of Circles

CODE_MAPPING = read_data(
    "data/utility/programCodeMappings.json")["title_to_code"]


def customise_spn_data():
    """ TODO: add docstring for this function"""

    data = read_data("data/scrapers/specialisationsFormattedRaw.json")

    customised_data: dict = {}  # TODO: specify type  # Dictionary for all customised data
    for spn in data.keys():
        if not any((prog in TEST_PROGS for prog in data[spn]["programs"])):
            continue

        formatted = data[spn]
        customised_data[spn] = {}
        initialise_spn(customised_data[spn], formatted)

        curriculum = []
        constraints = []
        for container in formatted["structure"]:
            # Build curriculum data and locate any constraints within curriculum

            if (
                container["description"]
                and not container["courses"]
                and not container["structure"]
            ):
                # If container lists no courses and has no nested curriculum
                # 'structure', then there is likely to be a constraint in the
                # 'description' field
                constraints.append(get_constraint(container))

            elif not 'Free Elective' in container['title'] or container.get('credits_to_complete') == 0:
                # Otherwise, the container includes course data which must be
                # parsed and extracted
                curriculum_item = {
                    "courses": {},
                    "title": container["title"],
                }
                curriculum_item["credits_to_complete"] = int(
                    get_credits(container))
                curriculum_item["core"] = is_core(
                    curriculum_item["title"].lower())

                # print(spn, curriculum_item["title"], curriculum_item["courses"])
                curriculum_item["levels"] = get_levels(
                    curriculum_item["title"].lower())
                curriculum_item["notes"] = get_notes(container["description"])

                if container["structure"]:
                    # Nested container exists containing curriculum data
                    get_nested_data(container["structure"], curriculum_item)
                else:
                    # No nested container containing curriculum data
                    get_courses(
                        curriculum_item["courses"],
                        container["courses"],
                        container["description"],
                    )

                # Add item to curriculum
                curriculum.append(curriculum_item)

        customised_data[spn]["course_constraints"] = constraints
        customised_data[spn]["curriculum"] = curriculum

    write_data(customised_data, "data/final_data/specialisationsProcessed.json")


def get_constraint(constraint_data: dict) -> dict:
    """
    Returns dict containing title and description of curriculum constraint;
    e.g. where students must complete at least X level 4 courses (such courses
    already being captured in the curriculum data)
    """
    return {
        "title": constraint_data["title"],
        "description": strip_tags(constraint_data["description"]),
    }


def strip_tags(text):
    """Strips HTML tags"""
    text = re.sub(r"<[^>]*?/>", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def initialise_spn(spn: dict, data: dict) -> None:
    """
    Initialises basic attributes of the specialisation.
    """
    spn["programs"] = data["programs"]
    spn["name"] = data["title"]
    spn["type"] = data["level"]
    spn["UOC"] = int(data["credit_points"])
    spn["code"] = data["code"]


def get_credits(container: dict) -> str:
    """
    Adds credit point requirements to curriculum item dict.
    Credit points exist either explicitly in the container's field
    "credit_points" or must be parsed from the "description" field.
    """
    if container["credit_points"]:
        return container["credit_points"]

    # No data in "credit_points" field, so parse plaintext "description"
    # Catches XX UOC, XX credits, XX Credit, etc.
    credits = re.search(r"(\d+) UOC|[cC]redit", container["description"])
    return credits.group(1) if credits else "0"

def is_core(title: str) -> bool:
    """
    Returns whether container is core.
    """
    return "core" in title.lower()


def get_levels(title: str) -> list[int]:
    """
    Parses 'title' to get curriculum levels of specialisation item.
    Level can be any combination of {1, 2, 3, 4, 5, 6, 7, 8, 9}.
    """
    levels: list[int] = []
    # s? \d[^ ]* captures cases like "Level 1/2", "Levels 1,2,3" and "Level 1-2"
    res = re.search(r"[Ll]evels? (\d[^ ]*)", title)

    if res:
        if "/" in res.group(1):
            # E.g. "Level 2/3 Mathematics Electives"
            multi_lvls = [int(lvl) for lvl in res.group(1).split("/")]
            levels.extend(multi_lvls)
            return levels

        # Otherwise single level is present
        found_level = int(res.group(1))
        levels.append(found_level)

        # Looks for 'higher' within 0 - 2 words of the level
        if re.match(r"[Ll]evels? (\d[^ ]*) ([^ ]+ ){0,2}higher", title):
            seq = list(range(found_level + 1, 10))
            levels.extend(seq)

    return levels


def get_notes(description: str) -> str:
    """Extracts any unique notes in the container description. While most
    course containers state 'Students must take X UOC of the following courses.',
    some include extra info after this line: e.g. 'Counting further VIP courses
    is only possible if etc.'"""

    # Non-greedy search to catch anything after first matching line
    res = re.search(
        r"Students must.*?following courses\.?([^.].+)", description)
    if res:  # Unique notes found
        return strip_tags(res.group(1))
    return ""


def get_nested_data(container: dict, curriculum_item: dict) -> None:
    """
    Adds curriculum data from nested container (the 'sub_container') into
    the curriculum item dict.
    """
    for sub_container in container:

        # Student may choose one of two courses
        if sub_container["title"] == "One of the following:":
            get_one_of_courses(
                sub_container["courses"], curriculum_item["courses"])

        else:
            get_courses(
                curriculum_item["courses"],
                sub_container["courses"],
                sub_container["description"],
            )


def get_one_of_courses(
    container_courses: dict[str, str], curriculum_courses: dict
) -> None:
    """
    Since tuples are not supported by JSON, current approach to 'one of
    the following' courses is to convert to key-value pair
    "COURSE1 or COURSE2": 2, the '2' representing that the key contains
    2 courses.
    """
    one_of_courses = ""
    course_added = False  # Flag value to identify where 'or' needs to be added
    for code in container_courses:
        if course_added:
            one_of_courses += " or "

        one_of_courses += code
        course_added = True
    curriculum_courses[one_of_courses] = list(container_courses.values())


def get_courses(
    curriculum_courses: dict, container_courses: dict[str, str], description: str
) -> None:
    """
    Adds courses from container to the customised curriculum course dict.
    """
    for course, title in container_courses.items():
        description = description + ""  # prevent unused variable error

        if "any course" in course.lower():
            course_processed = {"any course": "1"}
        elif "any level" in course.lower():
            # e.g. modify "any level 4 COMP course" to "COMP4"
            course_processed = process_any_level(course)
        else:
            course_processed = {course: title}
        curriculum_courses.update(course_processed)

def process_any_level(unprocessed_course: str) -> dict[str, str]:
    """
    Processes 'any level X PROGRAM NAME course' or 
    'any level X course/s offered by School of PROGRAM NAME'
    into 'CODEX'
    """
    # group 1 contains level number and group 3 contains program title
    # Note '?:' means inner parentheses is non-capturing group
    # COMP4XXx
    res = re.search(r"[lL]evel (\d)(?:/(\d))? courses? offered by (?:the )?School of((?: [^ \n]+)+)", unprocessed_course)
    if not res:
        res = re.search(r"[lL]evel (\d)(\/\d)? ((?:[^ ]+ )+)(course)?", unprocessed_course)
    if not res: # our regexes can't handle its power
        print("ERRR BY: ", unprocessed_course)
        return {}
    course_levels = [res.group(1).strip()]
    if res.group(2):
        course_levels.append(res.group(2))
    program_title = res.group(3).strip()

    # Removes any "(CODE)" text in program title
    # e.g. changes "Computer Science (COMP) "
    program_title = re.sub(r"\([A-Z]{4}\)", "", program_title)

    # Find CODE mapping; if unsuccessful, do nothing
    program_code = CODE_MAPPING.get(program_title, program_title)

    return {(program_code + course_level): unprocessed_course for course_level in course_levels}


if __name__ == "__main__":
    customise_spn_data()
