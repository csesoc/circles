"""
Program formats scraped / raw data by filtering out superfluous fields and
applying minor formatting to relevant fields. It creates the file
'programFormattedRaw.json'.

Within 'contentLets', relevant info includes:
 - creditPoints
 - studyLevel (e.g. 'undergraduate')
 - code (i.e. unique identifier for program)
 - title (e.g. 'Accounting')
 - data (see below)
 - curriculum_structure (see below)
 - additionalInfo

Step in the data's journey:
    [   ] Scrape raw data (programs_scraper.py)
    [ X ] Format scraped data (programs_formatting.py)
    [   ] Customise formatted data (programs_processing.py)
"""
import json
import re

from data.utility import data_helpers


def format_prg_data() -> None:
    """
    Get raw data for a program, format it and dump the output to
    programsFormatterRaw.json
    """
    # Get raw data
    raw_content = data_helpers.read_data("data/scrapers/programsPureRaw.json")
    # Initialise formatted data
    programs_formatted: dict[str, dict] = {}
    for program in raw_content:
        # Load summary infomation about program
        data = json.loads(program["data"])
        # Load infomation about program structure
        curriculum_structure = json.loads(program["CurriculumStructure"])

        # Setup dictionary and add data
        course_code = init_program(programs_formatted, data)
        try:
            add_data(programs_formatted, course_code, program, data, curriculum_structure)
        except KeyError as key_err:
            # we only care if it's not a research course lacking a program structure (there are about 100 such courses)
            if str(key_err) != "'container'" or program['studyLevelValue'] != 'rsch':
                raise key_err
            programs_formatted.pop(course_code)

    data_helpers.write_data(
        programs_formatted, "data/scrapers/programsFormattedRaw.json"
    )


def init_program(programs_formatted, data):
    """
    Initialises dictionary and assigns it to main programs dictionary
    """
    content = {  # type: ignore  # TODO: annotate this if you want
        "title": None,
        "code": None,
        "UOC": None,
        "studyLevel": None,
        "faculty": None,
        "duration": None,
        "academicOrg": None,
        "parentAcademicOrg": None,
        "CurriculumStructure": [],
        "structure": [],
        "description": None,
    }
    # Get course code
    course_code = data["course_code"]
    # Map course code to content
    programs_formatted[course_code] = content
    return course_code


def add_data(programs_formatted, course_code, program, data, curriculum_structure):
    """Assign values from raw data to dictionary"""

    # Get program info via code
    prog = programs_formatted[course_code]
    # Assign summary infomation from raw data
    prog["title"] = data.get("title")
    prog["code"] = data.get("course_code")
    prog["UOC"] = data.get("credit_points")
    prog["studyLevel"] = program.get("studyLevelURL")
    prog["faculty"] = data["parent_academic_org"]["value"]
    prog["duration"] = data.get("full_time_duration")
    prog["academicOrg"] = data.get("academic_org")["cl_id"]
    prog["parentAcademicOrg"] = data.get("parent_academic_org")["cl_id"]
    prog["overview"] = format_description(data.get("description"))
    prog["structure_summary"] = format_description(data.get("structure_summary"))
    # Assign infomation about program cirriculum
    format_curriculum(prog["structure"], curriculum_structure["container"])


def format_description(description: str) -> str:
    """
    (Lazily) formats description by getting rid of HTML tags, random unicode characters and multiple spaces.
    """
    # Get rid of any html tags
    description = re.sub(r"<.+?>" , " ", description)

    # Get rid of random unicode characters
    description = re.sub(r"[^\x00-\x7F]+", " ", description)

    # Get rid of double spaces and new lines mixed with spaces
    description = re.sub(r"  +", "\n", description)
    description = re.sub(r" *\n *", "\n", description)

    return description.strip()


def format_curriculum(curriculum_structure, currcontainer):
    """
    Filters through curiculum structure of program and saves neccesary
    infomation. Purpose of this is to make the information more readable
    """
    for item in currcontainer:
        # Information that we want to filter out
        info = {
            "vertical_grouping": item.get("vertical_grouping"),
            "title": item["title"],
            "description": format_description(item.get("description")),
            "credit_points": item.get("credit_points"),
            "credit_points_max": item.get("credit_points_max"),
            "parent_record": item["parent_record"]["value"],
            "container": [],
            "relationship": [],
            "dynamic_relationship": [],
        }
        # If course info is in this container level, it will be in the 'relationship'key
        if "relationship" in item and item["relationship"] != []:
            for course in item["relationship"]:
                if "container" in item and item["container"] != []:
                    # whats a fork bomb
                    format_curriculum(curriculum_structure, item["container"])
                item = {}
                item["academic_item_code"] = course.get("academic_item_code")
                item["academic_item_credit_points"] = course.get(
                    "academic_item_credit_points"
                )
                item["academic_item_name"] = course.get("academic_item_name")
                item["academic_item_type"] = course.get("academic_item_type")
                item["parent_record"] = course["parent_record"]["value"]
                info["relationship"].append(item)
        # Otherwise if it is in 'dynamic_relationship' key
        elif "dynamic_relationship" in item and item["dynamic_relationship"] != []:
            for course in item["dynamic_relationship"]:
                item = {}
                item["value"] = course["parent_record"]["value"]
                item["description"] = format_description(course.get("description"))
                info["dynamic_relationship"].append(item)

        elif "container" in item and item["container"] != []:
            # Course info in deeper container level, so recurse and repeat
            format_curriculum(info["container"], item["container"])

        # Append data to cirrculum structure
        curriculum_structure.append(info)

    return curriculum_structure


if __name__ == "__main__":
    format_prg_data()
