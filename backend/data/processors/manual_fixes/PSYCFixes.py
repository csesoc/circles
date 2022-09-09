"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Apply manual COMP fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.PSYCFixes
"""

from data.utility import data_helpers

CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")
PROCESSED = "processed"

COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")


def fix_conditions():
    """ Functions to apply manual fixes """
    CONDITIONS["PSYC1011"][PROCESSED] = PSYC_1011()
    CONDITIONS["PSYC1021"][PROCESSED] = PSYC_1021()
    CONDITIONS["PSYC2001"][PROCESSED] = PSYC_2001()
    CONDITIONS["PSYC2061"][PROCESSED] = PSYC_2061_2081()
    CONDITIONS["PSYC2071"][PROCESSED] = PSYC_2061_2081()
    CONDITIONS["PSYC2081"][PROCESSED] = PSYC_2061_2081()

    CONDITIONS["PSYC3011"][PROCESSED] = PSYC3011()
    CONDITIONS["PSYC3051"][PROCESSED] = PSYC3051_PSYC3241()
    CONDITIONS["PSYC3241"][PROCESSED] = PSYC3051_PSYC3241()
    CONDITIONS["PSYC3202"][PROCESSED] = PSYC_3202()
    CONDITIONS["PSYC3121"][PROCESSED] = PSYC3121_PSYC3301()
    CONDITIONS["PSYC3301"][PROCESSED] = PSYC3121_PSYC3301()
    CONDITIONS["PSYC3331"][PROCESSED] = PSYC3331()
    CONDITIONS["PSYC3361"][PROCESSED] = PSYC3361()
    CONDITIONS["PSYC4072"][PROCESSED] = PSYC4072_4073_4093_4103()
    CONDITIONS["PSYC4073"][PROCESSED] = PSYC4072_4073_4093_4103()
    CONDITIONS["PSYC4093"][PROCESSED] = PSYC4072_4073_4093_4103()
    CONDITIONS["PSYC4103"][PROCESSED] = PSYC4072_4073_4093_4103()


    data_helpers.write_data(
        CONDITIONS, "data/final_data/conditionsProcessed.json")
    data_helpers.write_data(COURSES, "data/final_data/coursesProcessed.json")

def PSYC_1011():
    """
    "original": "None<br/><br/>"
    "processed": "None"
    """

    return ""

def PSYC_1021():
    """
    "original": "Restricted to students currently enrolled in program 3632 Psychology (Honours) or 4721 Bachelor of Psychology (Honours) / Law<br/><br/>",
    "processed": "Restricted to currently program 3632 Psychology (Honours) || 4721 Bachelor of Psychology (Honours) / Law"
    """

    return "3632 || 4721"

def PSYC_2001():
    """
    "original": "Prerequisite: PSYC1001, PSYC1011, PSYC1111: Exclusion: GENS9003, GENS9004, GENS9005, GENS9007, GENS0005<br/><br/>",
    "processed": "PSYC1001, PSYC1011, PSYC1111:"
    """

    return "PSYC1001 && PSYC1011 && PSYC1111"

def PSYC_2061_2081():
    return "PSYC1001 && PSYC1011 && PSYC1111"


def PSYC2001():
    return "PSYC1001 && PSYC1011 && PSYC1111"


def PSYC3011():
    return "PSYC2001 && PSYC2061 && PSYC2071 && PSYC2081 && PSYC2101"


def PSYC3051_PSYC3241():
    return "PSYC2001 && PSYC2081"


def PSYC3121_PSYC3301():
    return "PSYC2001 && PSYC2061"

def PSYC_3202():
    """
    "original": "Prereq: PSYCs 2101, 2081, 2001<br/><br/>",
    "processed": "PSYCs 2101, 2081, 2001"
    """

    return "PSYC2101 && PSYC2081 && PSYC2001"


# TODO: JOEL: Another common case is where they have commas instead of &&.
# E.g. "PTRL3001,GEOS3321" or "PSYC2001 , PSYC2071" are examples
# Also, for PSYC specifically, "PSYCAH" isn't recognised?

def PSYC3211_PSYC3221_PSYC3311():
    return "PSYC2001 && PSYC2071"


def PSYC3331():
    return "(PSYC2001 || PSYC2061 || PSYC2101) || (HESC3504 && 3871)"


def PSYC3361():
    return "72UOC in PSYC && PSYC2001 && 75WAM"


def PSYC4072_4073_4093_4103():
    return "PSYCAH"


if __name__ == "__main__":
    fix_conditions()
