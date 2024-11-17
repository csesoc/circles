"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Apply manual COMP fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.COMPFixes
"""

from data.utility import data_helpers

CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")
PROCESSED = "processed"

COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")


def fix_conditions():
    """ Functions to apply manual fixes """

    CONDITIONS["COMP1911"][PROCESSED] = COMP_1911("COMP1911")
    CONDITIONS["COMP3431"][PROCESSED] = COMP_3431()
    CONDITIONS["COMP3821"][PROCESSED] = COMP_3821()
    CONDITIONS["COMP3900"][PROCESSED] = COMP_3900()
    CONDITIONS["COMP3901"] = COMP_3901_2(CONDITIONS["COMP3901"])
    CONDITIONS["COMP3902"] = COMP_3901_2(CONDITIONS["COMP3902"])
    CONDITIONS["COMP4141"][PROCESSED] = COMP_4141()
    CONDITIONS["COMP4951"] = COMP_4951(CONDITIONS["COMP4951"])
    CONDITIONS["COMP4952"][PROCESSED] = COMP_4952()
    CONDITIONS["COMP4953"][PROCESSED] = COMP_4953()
    CONDITIONS["COMP4961"][PROCESSED] = COMP_4961()
    CONDITIONS["COMP6445"][PROCESSED] = COMP_6445()
    CONDITIONS["COMP6447"][PROCESSED] = COMP_6447()
    CONDITIONS["COMP6721"][PROCESSED] = COMP_6721("COMP6721")
    CONDITIONS["COMP6841"][PROCESSED] = COMP_6841()
    CONDITIONS["COMP6845"][PROCESSED] = COMP_6845()
    CONDITIONS["COMP9242"][PROCESSED] = COMP_9242()
    CONDITIONS["COMP9301"] = COMP_9301(CONDITIONS["COMP9301"])
    CONDITIONS["COMP9302"] = COMP_9302(CONDITIONS["COMP9302"])

    codes = ["COMP9312", "COMP9313", "COMP9315"]
    for code in codes:
        CONDITIONS[code][PROCESSED] = COMP_9312_5()

    CONDITIONS["COMP9491"][PROCESSED] = COMP_9491()

    data_helpers.write_data(
        CONDITIONS, "data/final_data/conditionsProcessed.json")
    data_helpers.write_data(COURSES, "data/final_data/coursesProcessed.json")


def COMP_1911(code):
    """
    "original": "Prerequisite: Enrolment in a non-CSE major (no BINF, COMP, or SENG)<br/><br/>"

    "processed": ""
    """

    # Add exclusions to courseProcessed.json. Assumes that 'majors' includes
    # honours programs
    COURSES[code]["exclusions"]["COMP?1"] = 1
    COURSES[code]["exclusions"]["COMP?H"] = 1
    COURSES[code]["exclusions"]["BINF?1"] = 1
    COURSES[code]["exclusions"]["BINF?H"] = 1
    COURSES[code]["exclusions"]["SENGAH"] = 1

    # Then delete
    return ""


def COMP_3431():
    """
    "original": "Prerequisite: COMP2521 or COMP1927, and a WAM of at least 70<br/><br/>"

    "processed": "COMP2521 || COMP1927 && 70WAM"
    """
    return "(COMP2521 || COMP1927) && 70WAM"

def COMP_3821():
    # possible to remove
    """
    "original": "Prerequisite: A mark of at least 65 in COMP1927 or COMP2521<br/><br/>",
    "processed": "65GRADE in COMP1927 || COMP2521"
    """
    return "65GRADE in COMP1927 || 65GRADE in COMP2521"


def COMP_3900():
    """
    "original": "Prerequisite: COMP1531, and COMP2521 or COMP1927, and enrolled in a BSc Computer Science major with completion of 102 uoc.<br/><br/>"

    "processed": "COMP1531 && (COMP2521 || COMP1927) && 102UOC in (COMP?1 || COMPBH)"
    """

    # Note COMPBH is studied as a major stream in the BE(Hons)
    return "COMP1531 && (COMP2521 || COMP1927) && COMP# && 102UOC"


def COMP_3901_2(conditions):
    """
    "original": "Prerequisite: 80+ WAM in COMP, SENG or BINF courses, completion of all first and second year core requirements a CSE program, and agreement from a suitable CSE academic supervisor.<br/><br/>"

    "processed": "80WAM in (COMP || SENG || BINF)"

    "handbook_note": "You must complete all first and second year core requirements of
    a CSE program and obtain agreement from a suitable CSE academic supervisor
    to enrol in this course."
    """

    return {
        "original": conditions["original"],
        "processed": "80WAM in (COMP || SENG || BINF) && CORES in L1 && CORES in L2",
        "handbook_note": "You must obtain agreement from a suitable CSE academic supervisor to enrol in this course."
    }


def COMP_4141():
    """
    "original": "Prerequisite: MATH1081, and COMP1927 or COMP2521<br/><br/>",
    "processed": "MATH1081, && COMP1927 || COMP2521"
    """
    return "MATH1081 && (COMP1927 || COMP2521)"

def COMP_4951(conditions):
    """
    "original": "Prerequisite: Enrolled in a CSE BE (Hons) programs, completion of 126 UOC and completion of 3rd year core.<br/><br/>"

    "processed": "126UOC"

    "handbook_note": "You must be enrolled in a CSE BE (Hons) program and complete all third year core requirements to enrol in this course."
    """

    return {
        "original": conditions["original"],
        "processed": "126UOC && (BINF?H || SENGAH || COMP?H)",
        "handbook_note": "You must be enrolled in a CSE BE (Hons) program and complete all third year core requirements to enrol in this course."
    }


def COMP_4952():
    """
    "original": "Prerequisite: Completion of Research Thesis A (4951)<br/><br/>"

    "processed": "COMP4951"
    """
    return "COMP4951"


def COMP_4953():
    """
    "original": "Prerequisite: Completion of Research Thesis B (4952)<br/><br/>"

    "processed": "COMP4952"
    """
    return "COMP4952"


def COMP_4961():
    """
    "original": "Prerequisite: Enrolment in 4515 Computer Science (Hons) or 3779 Advanced Computer Science (Hons)<br/><br/>",

    "processed": "4515 || 3779"
    """
    return "4515 || 3779"


def COMP_6445():
    """
    "original": "Prerequisite: COMP3441 or COMP6441 or COMP6841, and COMP3231 or COMP3891<br/><br/>",
    "processed": "(COMP3441 || COMP6441 || COMP6841) && (COMP3231 || COMP3891)"
    """
    return "(COMP3441 || COMP6441 || COMP6841) && (COMP3231 || COMP3891)"


def COMP_6447():
    """
    "original": "Prerequisite: A mark of at least 65 in COMP6841, or a mark of at least 75 in COMP6441 or COMP3441.<br/><br/>",

    "processed": "65GRADE in COMP6841 || 75GRADE in COMP6441 || COMP3441"
    """
    return "65GRADE in COMP6841 || 75GRADE in (COMP6441 || COMP3441)"


def COMP_6721(code):
    """
    "original": "Pre-requisite: MATH1081 AND COMP2521 AND (not enrolled in SENGAH)<br/><br/>"

    "processed": "MATH1081 && COMP2521"
    """
    COURSES[code]["exclusions"]["SENGAH"] = 1
    return "MATH1081 && COMP2521"


def COMP_6841():
    """
    "original": "Prerequisite: Completion of 48 UOC, and COMP1927 or COMP2521<br/><br/>",

    "processed": "48UOC && (COMP1927 || COMP2521)"
    """
    return "48UOC && (COMP1927 || COMP2521)"


def COMP_6845():
    """
    "original": "Prerequisite: COMP3441 or COMP6441 or COMP6841, and COMP3231 or COMP3891<br/><br/>"

    "processed": "(COMP3441 || COMP6441 || COMP6841) && (COMP3231 || COMP3891)"
    """
    return "(COMP3441 || COMP6441 || COMP6841) && (COMP3231 || COMP3891)"


def COMP_9242():
    """
    "original": "Prerequisite: a mark of at least 75 in either COMP3231 or COMP3891.<br/><br/>"

    "processed": "75GRADE in (COMP3231 || COMP3891)"
    """
    return "75GRADE in (COMP3231 || COMP3891)"


def COMP_9301(conditions):
    """
    "original": "(COMP6441 OR COMP6841) AND (6 UOC from  (COMP6443, COMP6843, COMP6445, COMP6845, COMP6447)) AND enrolled in final term of program<br/><br/>",

    "processed": "(COMP6441 || COMP6841) && (COMP6443 || COMP6843 || COMP6445 || COMP6845 || COMP6447)",

    "handbook_note": "This course can only be taken in the final term of your program."
    """
    return {
        "original": conditions["original"],
        "processed": "(COMP6441 || COMP6841) && (COMP6443 || COMP6843 || COMP6445 || COMP6845 || COMP6447)",
        "handbook_note": "This course can only be taken in the final term of your program."
    }


def COMP_9302(conditions):
    """
    "original": "(COMP6441 OR COMP6841) AND (12 UOC from (COMP6443, COMP6843, COMP6445, COMP6845, COMP6447)) AND enrolled in final term of program<br/><br/>",

    "processed": "(COMP6441 || COMP6841) && (12UOC in (COMP6443 || COMP6843 || COMP6445 || COMP6845 || COMP6447))",

    "handbook_note": "This course can only be taken in the final term of your program."
    """
    return {
        "original": conditions["original"],
        "processed": "(COMP6441 || COMP6841) && (12UOC in (COMP6443 || COMP6843 || COMP6445 || COMP6845 || COMP6447))",
        "handbook_note": "This course can only be taken in the final term of your program."
    }


def COMP_9312_5():
    """
    "original": "Prerequisite: COMP1927 or COMP2521, and COMP3311<br/><br/>"

    "processed": "(COMP1927 || COMP2521) && COMP3311"
    """
    return "(COMP1927 || COMP2521) && COMP3311"


def COMP_9491():
    """
    "original": "Two prerequisite conditions:<br/>1. Students have taken:<br/>6 UOC from the following: COMP3411; and<br/>12 UOC from the following: COMP9444/COMP9417/COMP9517/COMP4418<br/>2. Students must have a WAM of 70 or higher<br/><br/>",

    "processed": "COMP3411 && 70WAM && 12UOC in (COMP9444 || COMP9417 || COMP9517 || COMP4418)"
    """
    return "COMP3411 && 70WAM && 12UOC in (COMP9444 || COMP9417 || COMP9517 || COMP4418)"


if __name__ == "__main__":
    fix_conditions()
