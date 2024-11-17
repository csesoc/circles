"""
Program formats scraped / raw data by filtering out superfluous fields and
applying minor formatting to relevant fields. It creates the file
'specialisationFormattedRaw.json'.

Within 'contentLets', relevant info includes:
 - creditPoints
 - studyLevel (e.g. 'undergraduate')
 - code (i.e. unique identifier for specialisation)
 - title (e.g. 'Accounting')
 - data (see below)
 - CurriculumStructure (see below)
 - additionalInfo
 - hb_enrolment_rules (i.e. constraints such as a maturity rule)

'data' includes, but is not limited to:
 - ELS requirements (not currently extracted)
 - structure summary
 - school detail
 - faculty detail
 - programs that the specialisation is available in
 - specialisation constraints (e.g. maturity rule)

'curriculumStructure' sets out the courses required to satisfy the
specialisation. Relevant info is located in a list of dictionaries titled
'container'. Each of these dictionaries includes:
 - title
 - description
 - relationship
 - dynamic_relationship
 - container

The required courses are either in 'relationship', 'dynamic_relationship',
or in deeper levels of 'container' (which has been accessed via recursion
in the below code).

Step in the data's journey:
    [   ] Scrape raw data (specialisationScraper.py)
    [ X ] Format scraped data (specialisationFormatting.py)
    [   ] Customise formatted data (specialisationProcessing.py)
"""

import json

from data.utility import data_helpers


def format_spn_data():
    """Extracts, processes and writes specialisation data to file"""

    raw_content = data_helpers.read_data("data/scrapers/specialisationsPureRaw.json")
    specialisations = {}
    for item in raw_content:

        # Unique identifier for the specialisation will be the primary key
        specCode = item["code"]

        # Setup dictionary and add data located in 'contentLets' key
        specialisations[specCode] = initialise_specialisation(item)

        # Load and process strings for further manipulation
        data = json.loads(item["data"])
        curriculum_structure = json.loads(item["CurriculumStructure"])

        # Add faculty and school
        add_school_details(specialisations[specCode], data)

        # Program availability seems be in one of two keys
        available_in = ["available_in_programs", "available_in_programs2021plus"]
        for key in available_in:
            get_available_in(data.get(key), specialisations, specCode)

        # Add any constraints on the specialisation
        specialisations[specCode]["constraints"] = get_constraints(data)

        # Add curriculum structure info by recursively traversing containers
        if "container" in curriculum_structure:
            get_structure(
                specialisations[specCode]["structure"],
                curriculum_structure["container"],
            )

    data_helpers.write_data(
        specialisations, "data/scrapers/specialisationsFormattedRaw.json"
    )


def initialise_specialisation(item):
    """Set up dictionary and add data in first level of 'contentLets'"""

    return {
        "title": item.get("title"),
        "code": item.get("code"),
        "study_level": item["studyLevel"].lower(),
        "level": item.get("level"),
        # Not all specialisations have credit points
        "credit_points": item.get("creditPoints"),
        "faculty": "",
        "school": "",  # Not all specialisations have a school
        "description": item.get("description"),
        "programs": [],  # Programs that the specialisation is available in
        # Not all specialisations have additional info
        "additional_info": item.get("additionalInfo"),
        "constraints": [],  # Not all specialisations have constraints
        "structure": [],  # This is where the required courses will sit
    }


def add_school_details(specialisation, data):
    """Adds faculty and school details, if any"""

    specialisation["faculty"] = data["faculty_detail"][0]["name"]
    if data["school_detail"]:  # Not all specialisations have a school
        specialisation["school"] = data["school_detail"][0]["name"]


def get_available_in(programs, specialisations, specCode):
    """Adds program codes that specialisation is available in"""

    if programs:
        for program in programs:
            specialisations[specCode]["programs"].append(program["assoc_code"])


def get_constraints(data):
    """Returns list of dictionaries containing any constraint details for specialisation"""

    constraints = []
    if data["hb_enrolment_rules"]:
        for rule in data["hb_enrolment_rules"]:
            # hb_enrolment_rules is a list of dictionaries containing each constraint
            constraint = {
                "type": rule["type"],
                "description": rule["enrolment_rule"][0]["description"],
            }
            constraints.append(constraint)

    return constraints


def get_structure(structure, curr_container):
    """Adds curriculum structure for specialisation"""

    for element in curr_container:

        structure.append(
            {
                "title": element["title"],
                "description": element.get("description"),
                "credit_points": element.get("credit_points"),
                "courses": {},
                "structure": [],  # Structure contains required courses for a
                # specialisation, and is represented as a list of dicitonaries
            }
        )
        # If course info is in this container level, it will either be in
        # the 'relationship' or 'dynamic_relationship' key
        if "relationship" in element and element["relationship"] != []:
            for course in element["relationship"]:
                if "academic_item_code" in course:
                    # Note use of '-1' to access last (i.e. current) dictionary in 'structure'
                    structure[-1]["courses"][course["academic_item_code"]] = course[
                        "academic_item_name"
                    ]
                elif "description" in course and course["description"] != "":
                    # Course info may be provided as a plaintext description if
                    # not provided as academic_item_code (e.g. 'any level 3 Finance course')
                    structure[-1]["courses"][course["description"]] = 1
                    # structure[-1]["courses"].append(course["description"])

        elif (
            "dynamic_relationship" in element and element["dynamic_relationship"] != []
        ):
            for course in element["dynamic_relationship"]:
                # dynamic_relationship provides course info as a plaintext description
                # structure[-1]["courses"].append(course["description"])
                structure[-1]["courses"][course["description"]] = 1

        elif "container" in element and element["container"] != []:
            # Course info in deeper container level, so recurse and repeat
            get_structure(structure[-1]["structure"], element["container"])


if __name__ == "__main__":
    format_spn_data()
