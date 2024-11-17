"""
Step in the course data's journey:
    [   ] Scrape raw data (coursesScraper.py)
    [   ] Format scraped data (coursesFormatting.py)
    [ X ] Customise formatted data (coursesProcessing.py)
"""

import re

from data.utility import data_helpers

# Fields to keep in the processed file without modification from coursesFormattedRaw.json
KEEP_UNEDITED = [
    "title",
    "code",
    "UOC",
    "level",
    "description",
    "study_level",
    "school",
    "faculty",
    "campus",
    "equivalents",
    "exclusions"
]

PROCESSED_COURSES: dict[str, dict] = {}


def process_course_data(year = None):
    """
    Read data from coursesFormattedRaw.json and process each course, noting
    their properties and write the final data to coursesProcessed.json
    """

    data = data_helpers.read_data(
        "data/scrapers/coursesFormattedRaw.json"
        if year is None else
        f"data/final_data/archive/formatted/{year}.json"
    )

    for code, course in data.items():
        processed = {k: v for k, v in course.items() if k in KEEP_UNEDITED}

        process_description(processed, course)
        format_types(processed)
        process_terms(processed, course)
        process_gen_ed(processed, course)
        process_exclusions(processed, course)
        process_enrolment_rules(processed, course)
        process_multi_term(processed, course)

        # Overwrite data file entry with the newly processed info
        data[code] = processed

    data_helpers.write_data(
        data,
        "data/final_data/coursesProcessed.json"
        if year is None else
        f"data/final_data/archive/processed/{year}.json"
    )

def process_description(processed: dict, formatted: dict) -> None:
    """Removes HTML tags from descriptions"""
    if formatted["description"]:
        processed["description"] = re.sub(
            r"<[^>]*?>", "", formatted["description"])


def format_types(processed: dict) -> None:
    """Converts things like UOC and Level to the right type (String->Int)"""
    if processed["UOC"] is not None:
        processed["UOC"] = int(processed["UOC"])

    if processed["level"] is not None:
        processed["level"] = int(processed["level"])
    else:
        processed["level"] = int(processed["code"][4])


def process_terms(processed: dict, formatted: dict) -> None:
    """Processes terms: e.g. 'Summer Term, Term 2' to ["T0", "T2"].
    Terms that do not conform to this (e.g. 'Summer Canberra') are left
    as is and will be modified at a later stage"""
    res = ""
    if formatted["calendar"] in ["3+", ""]:
        res = re.sub("Term ", "T", formatted["terms"])
    elif formatted["calendar"] == "Semester":
        res = re.sub("Semester ", "S", formatted["terms"])

    res = re.sub("Summer Term", "T0", res)
    res = re.sub("Summer Canberra", "SC", res)
    res_split = res.split(",")
    # Strip Remaining Spaces and discard empty strings
    res_set = set(item.strip(" ") for item in res_split)
    res_set.discard("")
    processed["terms"] = sorted(list(res_set))


def process_gen_ed(processed: dict, formatted: dict) -> None:
    """Processes whether the course is a gen ed. 0 for false and 1 for true"""
    if formatted["gen_ed"] == "false":
        processed["gen_ed"] = False
    else:
        processed["gen_ed"] = True

def process_exclusions(processed: dict, formatted: dict) -> None:
    """Parses exclusion string from enrolment rules"""

    # Extract exclusion string
    res = re.search(r"Excl.*?:(.*)",
                    formatted["enrolment_rules"], flags=re.IGNORECASE)
    if res:
        exclusion_str = res.group(1)

        # Remove prerequisite string (following exclusion string)
        exclusion_str = re.sub(
            r"Pre-?requisite.*", "", exclusion_str, flags=re.IGNORECASE
        )

        # Prepend MATH to 1131, 1141 and 1151
        math_codes = ["1131", "1141", "1151"]
        for code in math_codes:
            exclusion_str = re.sub(f" {code}", f" MATH{code}", exclusion_str)

        # Move courses into 'exclusions' field and remove from plaintext
        courses = re.findall(r"[A-Z]{4}\d{4}", exclusion_str)
        for course in courses:
            exclusion_str = re.sub(course, "", exclusion_str)
            processed["exclusions"][course] = 1

        # Move programs into 'exclusions' field and remove from plaintext
        programs = re.findall(r"\d{4}", exclusion_str)
        for program in programs:
            exclusion_str = re.sub(program, "", exclusion_str)
            processed["exclusions"][program] = 1

        exclusion_str = re.sub(
            r"(\d\d) units of credit", r"\1UOC", exclusion_str, flags=re.IGNORECASE
        )

        # Clean and add any remaining plaintext to 'exclusions' field
        patterns = ["<br/>", " ,", r"[.,]\s*$",
                    "^[.,]", "^and$", "enrolment in program"]
        exclusion_str = exclusion_str.strip()
        for pattern in patterns:
            exclusion_str = re.sub(pattern, "", exclusion_str)
        exclusion_str = exclusion_str.strip()

        # Leftover conjunctions should not be added
        no_conjunctions = re.sub("and", "", exclusion_str, flags=re.IGNORECASE)
        no_conjunctions = re.sub(
            "or", "", no_conjunctions, flags=re.IGNORECASE)
        if re.search(r"[A-Za-z]", no_conjunctions):
            processed["exclusions"]["leftover_plaintext"] = exclusion_str


def process_enrolment_rules(processed: dict, course: dict):
    """ removed br shit """
    processed["raw_requirements"] = re.sub(
        "<br/><br/>", "", course["enrolment_rules"])

def process_multi_term(processed: dict, formatted: dict) -> None:
    """ checks if a course is multiterm """
    processed["is_multiterm"] = any(attribute["type"] == "multi-term_course" for attribute in formatted["attributes"]) and int(formatted["UOC"]) % 6 != 0

if __name__ == "__main__":
    process_course_data()
