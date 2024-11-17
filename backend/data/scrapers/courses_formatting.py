"""
Step in the course data's journey:
    [   ] Scrape raw data (coursesScraper.py)
    [ X ] Format scraped data (coursesFormatting.py)
    [   ] Customise formatted data (coursesProcessing.py)
"""

import json

from data.utility import data_helpers

ALL_COURSES: dict = {}


def format_course_data(year = None):
    """Formats the raw course data"""
    raw_content = data_helpers.read_data("data/scrapers/coursesPureRaw.json"
        if year is None else
        f"data/final_data/archive/raw/{year}.json"
    )

    for course in raw_content:
        # Add basic details to course dict
        formatted_course = initialise_course(course)

        # Load value in 'data' string
        course_data = json.loads(course["data"])

        # Scrape details from 'data' value
        get_faculty(formatted_course, course_data)
        get_offering(formatted_course, course_data)
        get_field(formatted_course, course_data)
        get_attributes(formatted_course, course_data)
        get_equivalents(formatted_course, course_data)
        get_exclusions(formatted_course, course_data)
        get_enrolment_rules(formatted_course, course_data)

        if formatted_course["study_level"] == "Undergraduate" or course["code"] not in ALL_COURSES:
            ALL_COURSES[course["code"]] = formatted_course

    data_helpers.write_data(
        ALL_COURSES,
        "data/scrapers/coursesFormattedRaw.json"
        if year is None else
        f"data/final_data/archive/formatted/{year}.json"
    )


def initialise_course(raw: dict) -> dict:
    """Retrieves standard details for course"""
    return {
        "title": raw.get("title"),
        "code": raw.get("code"),
        "UOC": raw.get("creditPoints", 0),
        "gen_ed": raw.get("generalEducation"),
        "level": raw.get("levelNumber"),
        "description": raw.get("description", ""),
        "study_level": raw.get("studyLevel"),
    }


def get_faculty(formatted: dict, raw: dict) -> None:
    """Retrieves faculty details for course"""
    if raw["school_detail"]:
        formatted["school"] = raw["school_detail"][0].get("name")
    if raw["faculty_detail"]:
        formatted["faculty"] = raw["faculty_detail"][0].get("name")


def get_offering(formatted: dict, raw: dict) -> None:
    """Retrieves campus and semester details"""
    formatted["campus"] = raw.get("campus")
    formatted["terms"] = raw["offering_detail"].get("offering_terms")
    formatted["calendar"] = raw["academic_calendar_type"].get("value")


def get_attributes(formatted: dict, raw: dict) -> None:
    """Retrieves course attributes and creates a dictionary containing
    the type of attribute and its description"""
    formatted["attributes"] = []
    if not raw["attributes"]:
        # Not all courses have attributes, so this might be an empty list
        return

    for attribute in raw["attributes"]:
        formatted["attributes"].append(
            {
                "type": attribute["code"],  # e.g. 'general_education'
                "description": attribute["description"],
            }
        )


def get_field(formatted: dict, raw: dict) -> None:
    """Retrieves Field of Education code"""
    formatted["field_of_education"] = raw["asced_detailed"].get("value")


def get_equivalents(formatted: dict, raw: dict) -> None:
    """Retrieves equivalent courses, if any, and puts their code in a dict with
    an arbitrary value (to make it hashable). For example, "DPST1091": 1"""
    formatted["equivalents"] = {}
    if not raw["eqivalents"]:
        # NB: handbook has typo 'eqivalents' for equivalents key for all courses
        return

    for equiv in raw["eqivalents"]:
        formatted["equivalents"][equiv["assoc_code"]] = 1


def get_exclusions(formatted: dict, raw: dict) -> None:
    """Retrieves exclusion courses, if any, and puts their code in a dict with
    an arbitrary value (to make it hashable). For example, "DPST1091": 1"""
    formatted["exclusions"] = {}
    if not raw["exclusion"]:
        return

    for excl in raw["exclusion"]:
        formatted["exclusions"][excl["assoc_code"]] = 1


def get_enrolment_rules(formatted: dict, raw: dict) -> None:
    """Retrieves enrolment rules, if any"""
    formatted["enrolment_rules"] = ""
    if raw["enrolment_rules"]:
        # There could potentially be multiple enrolment rules (e.g. SENG4920)
        formatted_rule = ""
        for rule in raw["enrolment_rules"]:
            formatted_rule += rule.get("description")

        formatted["enrolment_rules"] = formatted_rule


if __name__ == "__main__":
    format_course_data()
