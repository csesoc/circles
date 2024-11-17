"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Apply manual COMP fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.SENGFixes
"""

from data.utility import data_helpers

CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")
PROCESSED = "processed"

COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")


def fix_conditions():
    """ Functions to apply manual fixes """

    CONDITIONS["SENG2021"][PROCESSED] = SENG_2021()
    CONDITIONS["SENG2991"] = SENG_2991(CONDITIONS["SENG2991"])
    # Removed
    # CONDITIONS["SENG3991"] = SENG_3991(CONDITIONS["SENG3991"])
    # CONDITIONS["SENG3992"] = SENG_3992(CONDITIONS["SENG3992"])
    if "SENG4920" in CONDITIONS:
        CONDITIONS["SENG4920"][PROCESSED] = SENG_4920()

    data_helpers.write_data(
        CONDITIONS, "data/final_data/conditionsProcessed.json")
    data_helpers.write_data(COURSES, "data/final_data/coursesProcessed.json")


def SENG_2021():
    """
    "original": "Prerequisite:  SENG1031 or COMP1531, and enrolment in a BE or BE(Hons) Software Engineering major.<br/><br/>",

    "processed": "SENG1031 || COMP1531 && (SENG?1 || SENG?H)"
    """

    return "(SENG1031 || COMP1531) && ENGG#"


def SENG_2991(conditions):
    """
    "original": "Currently enrolled in Program 3707 in the SENGAH stream <br/>and in an approved workplace arrangement <br/>and completed COMP1511, COMP1531 and COMP2521.<br/><br/>"

    "processed": "COMP1511 && COMP1531 && COMP2521 && 3707 && SENGAH"

    "handbook_note": "Must be in an approved workplace arrangement"
    """

    return {
        "original": conditions["original"],
        "processed": "COMP1511 && COMP1531 && COMP2521 && 3707 && SENGAH",
        "handbook_note": "Must be in an approved workplace arrangement"
    }


def SENG_3991(conditions):
    """
    "original": "Currently enrolled in Program 3707 in the SENGAH stream and in the Co-op program<br/>and completed SENG2011 and SENG2021 and DESN2000 and COMP2511 and COMP2041.<br/><br/>Successful completion of SEN2991 and attendance of IT Reflection Workshop (facilitated by Co-op Program) are a<br/>prerequisite for this course.<br/><br/>"

    "processed": "3707 && SENGAH && SENG2011 && SENG2021 && DESN2000 && COMP2511 && COMP2041 && SENG2991"

    "handbook_note": "Must currently be enrolled in the Co-op program and completed attendance of IT Reflection Workshop (facilitated by Co-op Program)"
    """

    return {
        "original": conditions["original"],
        "processed": "3707 && SENGAH && SENG2011 && SENG2021 && DESN2000 && COMP2511 && COMP2041 && SENG2991",
        "handbook_note": "Must currently be enrolled in the Co-op program and completed attendance of IT Reflection Workshop (facilitated by Co-op Program)"
    }


def SENG_3992(conditions):
    """
    "original": "Currently enrolled in Program 3707 in the SENGAH stream and in the Co-op program<br/>and completed SENG3011.<br/><br/>Successful completion of SEN2991 and SENG3991are a prerequisite for this course<br/><br/>",

    "processed": "3707 && SENGAH && SENG3011 && SENG2991 && SENG3991"

    "handbook_note": "Must currently be enrolled in the Co-op program"
    """
    return {
        "original": conditions["original"],
        "processed": "3707 && SENGAH && SENG3011 && SENG2991 && SENG3991",
        "handbook_note": "Must currently be enrolled in the Co-op program"
    }

def SENG_4920():
    """
        "original": "<br/>Completed more than or equal to 144 UOC in SENGAH, BINFAH or COMPBH<br/><br/>Prerequisite: COMP2511<br/><br/>",
        "processed": "more than || equal to 144UOC in SENGAH, BINFAH || COMPBH COMP2511"
    """
    return "144UOC && COMP2511 && (SENGAH || BINFAH || COMPBH)"

if __name__ == "__main__":
    fix_conditions()
