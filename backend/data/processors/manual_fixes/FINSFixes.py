"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Copy this into a new file for the relevant faculty's fixes:
e.g. COMPFixes.py, ACCTFixes.py, PSYCFixes.py

Apply manual FINS fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.FINSFixes
"""

from data.utility import data_helpers

# Reads conditionsProcessed dictionary into 'CONDITIONS'
CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")
PROCESSED = "processed"

# Reads coursesProcessed dictionary into 'COURSES' (for updating exclusions)
COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")


def fix_conditions():
    """ Functions to apply manual fixes """

    CONDITIONS["FINS2101"][PROCESSED] = FINS_2101()
    CONDITIONS["FINS2622"][PROCESSED] = FINS_2622()
    CONDITIONS["FINS3202"][PROCESSED] = FINS_3202_3303()
    CONDITIONS["FINS3303"][PROCESSED] = FINS_3202_3303()
    CONDITIONS["FINS3626"][PROCESSED] = FINS_3626()
    CONDITIONS["FINS3630"][PROCESSED] = FINS_3630()
    CONDITIONS["FINS3645"][PROCESSED] = FINS_3645()
    CONDITIONS["FINS3646"][PROCESSED] = FINS_3646()
    CONDITIONS["FINS4774"][PROCESSED] = FINS_4774()
    CONDITIONS["FINS4776"][PROCESSED] = FINS_4776_7_9()
    CONDITIONS["FINS4777"][PROCESSED] = FINS_4776_7_9()
    CONDITIONS["FINS4779"][PROCESSED] = FINS_4776_7_9()
    CONDITIONS["FINS4792"][PROCESSED] = FINS_4792()

    # Updates the files with the modified dictionaries
    data_helpers.write_data(
        CONDITIONS, "data/final_data/conditionsProcessed.json")
    data_helpers.write_data(COURSES, "data/final_data/coursesProcessed.json")


def FINS_2101():
    """
    "original": "Enrolled in plan FINSD13554 or in FINSBH3565<br/><br/>",

    "processed": "plan FINSD13554 || in FINSBH3565"
    """

    # Legacy Handbook
    return "FINSD13554 || FINSBH3565"


def FINS_2622():
    """
    "original": "Prerequisite or co-requisite:FINS1612 and FINS2624<br/><br/>",

    "processed": "|| [FINS1612 && FINS2624]"
    """

    return "[FINS1612 || FINS2618] && FINS2624"


def FINS_3202_3303():
    """
    "original": "Prerequisite: FINS2101 and enrolled in plan FINSD13554 or FINSBH3565<br/><br/>",

    "processed": "FINS2101 && plan FINSD13554 || FINSBH3565"
    """

    # Legacy Handbook
    return "FINS2101 && (FINSD13554 || FINSBH3565)"


def FINS_3626():
    """
    "original": "Prerequisite: COMM1140 or ACCT1511 and COMM1180 or (COMM1140 and ECON1102) or FINS1613<br/><br/>",

    """

    return "(COMM1140 || ACCT1511) && (COMM1180 || (COMM1140 && ECON1102) || FINS1613)"


def FINS_3630():
    """
    "original": "FINS1612/FINS2618, and, COMM1180 OR (COMM1140 and ECON1102) OR FINS1613<br/><br/>",
    """

    return "(FINS1612 || FINS2618) && (COMM1180 || (COMM1140 && ECON1102) || FINS1613)"


def FINS_3645():
    """
    "original": "Pre-requisite: FINS1612/2618;  OR enrolment in a Business Analytics Major (COMMJ1) and completion of COMM1180 or FINS1613 or (COMM1140 and ECON1102)<br/><br/>",

    """

    return "(FINS1612 || FINS1618) || (COMMJ1 && (COMM1180 || FINS1613 || (COMM1140 && ECON1102)))"

def FINS_3646():
    """
    "original": "Pre-requisite: FINS1612/FINS2618 OR (Business Analytics Major (COMMJ1) and COMM1180 OR FINS1613 OR (COMM1140 and ECON1102)<br/><br/>",

    "processed": "FINS1612 || (Business Analytics Major (COMMJ1) && COMM1180 || FINS1613"
    """

    return "FINS1612 || FINS2618 || (COMMJ1 && (COMM1180 || FINS1613 || (COMM1140 && ECON1102)))"


def FINS_4774():
    """
    "original": "Prerequisite: Must be enrolled in specialisation FINSAH4501 or FINSBH3565; or program 4520.<br/><br/>",

    "processed": "Must be specialisation FINSAH4501 || FINSBH3565; || program 4520."
    """

    return "((FINSAH && 4501) || (FINSBH && 3565) || 4520)"


def FINS_4776_7_9():
    """
    "original": "Prerequisite: Must be enrolled in specialisation FINSAH4501 or FINSBH3565; or program 4520",

    "processed": "Must be specialisation FINSAH4501 || FINSBH3565; || program 4520."
    """

    return "((FINSAH && 4501) || (FINSBH && 3565) || 4520)"


def FINS_4792():
    """
    "original": "Prerequisite: Must be enrolled in specialisation FINSAH4501 or FINSBH3565;  or program 4520.<br/><br/>",

    "processed": "Must be specialisation FINSAH4501 || FINSBH3565; || program 4520."
    """

    return "((FINSAH && 4501) || (FINSBH && 3565) || 4520) "


if __name__ == "__main__":
    fix_conditions()
