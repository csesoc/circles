"""
Program extracts raw data for Programs and place data in file
'coursesPureRaw.json', ready for formatting.

Step in the data's journey:
    [ X ] Scrape raw data (gened_scraper.py)
    [   ] Format scraped data
    [   ] Customise formatted data
"""

import json

import requests
from data.scrapers.courses_scraper import TOTAL_COURSES
from data.scrapers.payload import HEADERS, create_payload_gened
from data.utility import data_helpers

URL = "https://www.handbook.unsw.edu.au/api/es/search?appliedFilters="

def scrape_gened_data(year=None):
    """
    Retrieves gen ed data for all undergraduate programs
    Stores in genedPureRaw.json as list of course codes for each program code in programsFormattedRaw.json
    """
    faculty_list = set()
    gened_raw = {}
    cl_id = ""
    academicOrg = ""

    programs_formatted = data_helpers.read_data("data/scrapers/programsFormattedRaw.json")
    for program_code, program in programs_formatted.items():
        faculty = program["faculty"]
        faculty_list.add(faculty)

        if faculty in ["Faculty of Arts, Design and Architecture", "Faculty of Law and Justice"]:
            academicOrg = "academicOrg"
        else:
            academicOrg = "parentAcademicOrg"
        cl_id = program[academicOrg]

        try:
            resp = requests.get(
                URL,
                data=json.dumps(create_payload_gened(TOTAL_COURSES, "unsw_psubject", cl_id, academicOrg, year)),
                headers=HEADERS,
                timeout=60 * 5
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"{err}+ Failed at program: {program_code}")

        r = requests.post(
            URL,
            data=json.dumps(create_payload_gened(TOTAL_COURSES, "unsw_psubject", cl_id, academicOrg, year)),
            headers=HEADERS,
            timeout=60 * 5
        )
        new_gened_courses_raw = r.json()["contentlets"]

        # gen eds by program code
        courses = {}
        for course in new_gened_courses_raw:
            courses[course["code"]] = course["title"]
        gened_raw[program["code"]] = courses
    data_helpers.write_data(
        gened_raw,
        "data/scrapers/genedPureRaw.json"
        if year is None else
        f"data/final_data/archive/raw/{year}.json"
    )

if __name__ == "__main__":
    scrape_gened_data()
