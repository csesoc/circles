"""
https://github.com/csesoc/Circles/wiki/Manual-Fixes-to-Course-Prerequisites

Apply manual [code] fixes to processed conditions in conditionsProcessed.json so
that they can be fed into algorithms.

If you make a mistake and need to regenerate conditionsProcessed.json, then you
can run:
    python3 -m data.processors.conditionsPreprocessing

To then run this file:
    python3 -m data.processors.manualFixes.CHEMFixes
"""

from data.utility import data_helpers

# Reads conditionsProcessed dictionary into 'CONDITIONS'
CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")
PROCESSED = "processed"

# Reads coursesProcessed dictionary into 'COURSES' (for updating exclusions)
COURSES = data_helpers.read_data("data/final_data/coursesProcessed.json")


def fix_conditions():
    """ Functions to apply manual fixes """
    CONDITIONS["CHEM1041"] = CHEM_1041(CONDITIONS["CHEM1041"])
    CONDITIONS["CHEM1051"][PROCESSED] = CHEM_1051()
    CONDITIONS["CHEM1061"][PROCESSED] = CHEM_1061()
    CONDITIONS["CHEM1521"][PROCESSED] = CHEM_1521()
    CONDITIONS["CHEM1151"][PROCESSED] = CHEM_1151()
    CONDITIONS["CHEM1829"][PROCESSED] = CHEM_1829()
    if "CHEM1831" in CONDITIONS:
        CONDITIONS["CHEM1831"][PROCESSED] = CHEM_1831()
    CONDITIONS["CHEM1832"][PROCESSED] = CHEM_1832()
    CONDITIONS["CHEM1777"][PROCESSED] = CHEM_1777()
    CONDITIONS["CHEM2051"][PROCESSED] = CHEM_2051()
    CONDITIONS["CHEM2521"] = CHEM_2521(CONDITIONS["CHEM2521"])
    CONDITIONS["CHEM2701"][PROCESSED] = CHEM_2701()
    CONDITIONS["CHEM3051"][PROCESSED] = CHEM_3051()
    CONDITIONS["CHEM6701"][PROCESSED] = CHEM_6701()

    # Updates the files with the modified dictionaries
    data_helpers.write_data(
        CONDITIONS, "data/final_data/conditionsProcessed.json")
    data_helpers.write_data(COURSES, "data/final_data/coursesProcessed.json")

def CHEM_1041(condition):
    """
        "original": "Prerequisite: CHEM1031, or CHEM1011 with a credit or above.<br/><br/>Prerequisite: Must be enrolled in a program with the option of a CHEM major<br/><br/>",
        "processed": "CHEM1031 || CHEM1011 && a credit . Must be a program && the option of a CHEM major"
    """
    return {
        "original" : condition["original"],
        "processed":"(CHEM1031 || 65GRADE in CHEM1011)",
        "handbook_note": "Must be a program && the option of a CHEM major"
    }

def CHEM_1051():
    """
        "original": "Prerequisite: Enrolment in the Bachelor of Medicinal Chemistry (3999 or 3992) or Bachelor of Medicinal Chemistry/Law program<br/><br/>",
        "processed": "Enrolment in the Bachelor of Medicinal Chemistry (3999 || 3992) || Bachelor of Medicinal Chemistry/LAWS#"
    """
    return "MCHM#"

def CHEM_1832():
    """
    "original": "Enrolment in 3894 Nutrition/Dietetics and Food Innovation or 3895 Pharmaceutical Medicine/Pharmacy<br/><br/>",
    "processed": "Enrolment in 3894 Nutrition/Dietetics && Food Innovation || 3895 Pharmaceutical Medicine/Pharmacy"
    """
    return "3894 || 3895"

def CHEM_1061():
    """
        "original": "Prerequisite: Enrolment in the Bachelor of Medicinal Chemistry (3992 or 3999) program and completion of either CHEM1051 or CHEM1031 or CHEM1011 with a credit or above.<br/><br/>",
        "processed": "Enrolment in the Bachelor of Medicinal Chemistry (3992 || 3999) program && CHEM1051 || CHEM1031 || CHEM1011 && a credit"
    """
    return "MCHM# && (CHEM1051 || CHEM1031 || 65GRADE in CHEM1011)"

def CHEM_1829():
    """
        "original": "Prerequisite: CHEM1011, and enrolment in 3181, 3182, 3952 or a Vision Science major.<br/><br/>",
        "processed": "CHEM1011 && enrolment in 3181 || 3182 || 3952 || a Vision Science major"
    """
    return "CHEM1011 && (3181 || 3182 || 3952 || VISN?1)"

def CHEM_1831():
    """
        "original": "None<br/><br/>Must be enrolled in Exercise Physiology (3871) <br/><br/>",
        "processed": "Must be Exercise Physiology (3871)"
    """
    return "3871"

def CHEM_1151():
    """
        "original": "Enrolment in Medicinal Chemistry (3992) or (3999) or 4755<br/><br/>",
        "processed": "Enrolment in Medicinal Chemistry (3992) || (3999) || 4755"
    """
    return "MCHM# || 4755"


def CHEM_1521():
    """
        "original": "Pre-req of Prerequisite: CHEM1011 Chemistry 1A or equivalent. Exclusion: CHEM1021<br/><br/>",
        "processed": "of CHEM1011 Chemistry 1A || equivalent"
    """
    return "CHEM1011"

def CHEM_1777():
    """
        "original": "Presumed knowledge is Year 10 General Science.<br/><br/>",
        "processed": "knowledge is Year 10 General Science"
    """
    return ""

def CHEM_2051():
    """
        "original": "Enrolment into 3999 Medicinal Chemistry or 3895 Pharmaceutical Medicine/Pharmacy<br/><br/>Pre-requisites: PHRM1021 or CHEM1021 or CHEM1041 or CHEM1061 <br/><br/>",
        "processed": "Enrolment into 3999 Medicinal Chemistry || 3895 Pharmaceutical Medicine/Pharmacy PHRM1021 || CHEM1021 || CHEM1041 || CHEM1061"
    """
    return "3999 || 3895 && (PHRM1021 || CHEM1021 || CHEM1041 || CHEM1061)"

def CHEM_2701():
    """
        "original": "First year chemistry is a prerequisite. One of the following courses must have been completed prior to enrolment: <br/> - CHEM1021 -- Chemistry 1B <br/> - CHEM1041/1061 -- Higher Chemistry 1B<br/> - CHEM1821 -- Engineering Chemistry 1B<br/> - CHEM1829 -- Biological Chemistry for Optometry Students<br/><br/>",
        "processed": "First year chemistry is a . One of the following courses must have been : - CHEM1021 -- Chemistry 1B - CHEM1041/1061 -- Higher Chemistry 1B - CHEM1821 -- Engineering Chemistry 1B - CHEM1829 -- Biological Chemistry for Optometry"
    """
    return "CHEM1021 || CHEM1041 || CHEM1061 || CHEM1821 || CHEM1829"

def CHEM_2521(condition):
    """
        "original": "This is the main Level 2 Organic Chemistry course taught within the School of Chemistry.<br/>It assumes knowledge of CHEM1011 and CHEM1021 or CHEM1031 and CHEM1041 or CHEM1051 and CHEM1061, AND CHEM2041. It is a core element in Chemistry major programs. It is also required for industrial chemistry, biochemistry and medicinal chemistry programs.<br/><br/>",
        "processed": "This is the main L2 Organic Chemistry course taht within the School of Chemistry. It assumes knowledge of CHEM1011 && CHEM1021 || CHEM1031 && CHEM1041 || CHEM1051 && CHEM1061 && CHEM2041. It is a core element in Chemistry major programs. It is also required for industrial chemistry, biochemistry && MCHM#"
    """

    return {
        'original': condition['original'],
        'processed' : '(CHEM1011 && CHEM1021) || (CHEM1031 && CHEM1041) || (CHEM1051 && CHEM1061) && CHEM2041',
        'handbook_note': 'This is the main Level 2 Organic Chemistry course taught within the School of Chemistry.<br/> It is a core element in Chemistry major programs. It is also required for industrial chemistry, biochemistry and medicinal chemistry programs'
    }


def CHEM_3051():
    """
        "original": "Must be enrolled in Program 3999<br/><br/>Pre-requisite: CHEM3021<br/><br/>",
        "processed": "Must be Program 3999 CHEM3021"
    """
    return "3999 && CHEM3021"

def CHEM_6701():
    """
        "original": "12 UOC of CHEM2011, CHEM2021, CHEM2031, CHEM2839, CHEM2041 & CHEM2828<br/><br/>",
        "processed": "12UOC of CHEM2011, CHEM2021, CHEM2031, CHEM2839, CHEM2041 && CHEM2828"
    """
    return "12UOC in (CHEM2011 || CHEM2021 || CHEM2031 || CHEM2839 || CHEM2041 || CHEM2828)"


if __name__ == "__main__":
    fix_conditions()
