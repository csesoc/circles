"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Copy this into a new file for the relevant faculty's fixes:
e.g. COMPFixes.py, ACCTFixes.py, PSYCFixes.py

Apply manual [code] fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.[CODE]Fixes
"""

from data.utility import dataHelpers

# Reads conditionsProcessed dictionary into 'CONDITIONS'
CONDITIONS = dataHelpers.read_data("data/finalData/conditionsProcessed.json")
PROCESSED = "processed"

# Reads coursesProcessed dictionary into 'COURSES' (for updating exclusions)
COURSES = dataHelpers.read_data("data/finalData/coursesProcessed.json")

def fix_conditions():
    """ Functions to apply manual fixes """

    # TODO: call your functions here
    for course in ("MATS4500", "MATS4501", "MATS4503", "MATS4504", "MATS4505"):
        CONDITIONS[course][PROCESSED] = MATS_4500_4501_4503_4504_4505()


    CONDITIONS["MATS5003"][PROCESSED] = MATS_5003()

    # Updates the files with the modified dictionaries
    dataHelpers.write_data(
        CONDITIONS, "data/finalData/conditionsProcessed.json")
    dataHelpers.write_data(COURSES, "data/finalData/coursesProcessed.json")

def MATS_4500_4501_4503_4504_4505():
    """
    "original": "Prerequisite: Enrolled in Materials Science Honours Plan<br/><br/>",
    "processed": "Materials Science Honours Plan"
    """
    # TODO: JOEL: Similar to one of the the MATHFixes.py function, it doesn't like this
    return "MATS?H"

def MATS_5003():
    """
    "original": "Prerequisite : MATS5001<br/><br/>",
    "processed": ": MATS5001"
    """

    return "MATS5001"



if __name__ == "__main__":
    fix_conditions()
