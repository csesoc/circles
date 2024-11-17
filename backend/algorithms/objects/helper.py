""" HELPER FUNCTIONS TO DETERMINE THE TYPE OF A GIVEN TEXT """

import json
import re
from enum import Enum
from sys import exit


class Logic(Enum):
    """ Logic Keywords """
    AND = "&&"
    OR = "||"


def is_course(text) -> bool:
    """ If the text is a course """
    return bool(re.match(r"^[A-Z]{4}\d{4}$", text, flags=re.IGNORECASE))


def is_uoc(text) -> bool:
    """ If the text is UOC """
    return bool(re.match(r"^\d+UOC$", text, flags=re.IGNORECASE))


def get_uoc(text: str) -> int:
    """ Given a text in the format of ???UOC, will extract the uoc and return as an int """
    uoc_str = re.match(r"^(\d+)UOC$", text, flags=re.IGNORECASE)
    if not uoc_str:
        raise KeyError("trying to fetch UOC where it doesnt exist!")
    return int(uoc_str.group(1))


def get_level_category(text: str) -> int:
    """ will extract the L? and return as an int """
    level_str = re.match(r"^L([0-9])$", text, flags=re.IGNORECASE)
    if not level_str:
        raise KeyError("trying to fetch level category where it doesnt exist!")
    return int(level_str.group(1))


def get_course_category(text: str) -> str:
    """ will extract the course category """
    level_str = re.match(r"^([A-Z]{4})$", text, flags=re.IGNORECASE)
    if not level_str:
        raise KeyError("trying to fetch course category where it doesnt exist!")
    return level_str.group(1)


def is_wam(text) -> bool:
    """ If the text is WAM """
    return bool(re.match(r"^\d+WAM$", text, flags=re.IGNORECASE))


def get_wam(text) -> int:
    """ Given a text in the format of ???WAM, will extract the wam and return as a int """
    wam_str = re.match(r"^(\d+)WAM$", text)
    if not wam_str:
        raise KeyError("trying to fetch WAM where it doesnt exist!")
    return int(wam_str.group(1))


def is_grade(text) -> bool:
    """ If the text is GRADE """
    return bool(re.match(r"^\d+GRADE$", text, flags=re.IGNORECASE))


def get_grade(text) -> int:
    """
    Given a text in the format of ???GRADE,
    will extract the grade and return as a int
    """
    grade_str = re.match(r"^(\d+)GRADE$", text)
    if not grade_str:
        raise KeyError("trying to fetch GRADE where it doesnt exist!")
    return int(grade_str.group(1))


def is_program(text) -> bool:
    """ Determines if the text is a program code """
    return bool(
        re.match(r"^\d{4}$", text)
        or re.match(r"^[A-Z]{5}\d{5}", text)
        or re.match(r"^[A-Z]{6}\d{4}", text)
    )


def is_program_type(program: str) -> bool:
    """ Determines if the input is of type `program` """
    return bool(re.match(r"^[A-Z]{4}#$", program, flags=re.IGNORECASE))


def is_specialisation(text) -> bool:
    """ Determines if the text is a specialisation code """
    return bool(re.match(r"^[A-Z?]{5}[0-9H?]$", text, flags=re.IGNORECASE))



# ======================================================== #
# ========= HELPER FUNCTIONS FOR UTILITY PURPOSES ======== #
# ======================================================== #


def read_data(file_name):
    """ Reads data from a json file and returns it """
    try:
        with open(file_name, "r", encoding="utf8") as input_file:
            return json.load(input_file)
    except (IOError, OSError):
        print(f"File {file_name} not found")
        exit(1)
