"""
Scrapes program codes and produces JSON file with two dictionaries,
one mapping program code to program title and the other the opposite.
"""

import json

import requests


def get_mappings():
    """Build mappings between program code and name"""

    code_to_title = {}
    title_to_code = {}

    data = request_data()
    for program in data:
        formatted_title = program["title"][6:]  # slice off code in title

        code_to_title[program["code"]] = formatted_title
        title_to_code[formatted_title] = program["code"]

    write_to_file(code_to_title, title_to_code)


def request_data():
    """Requests and returns jsonified data"""

    r = requests.get(
        "https://www.handbook.unsw.edu.au/api/content/render/false/query/+contentType:unsw_peducational_area +conHost:f59fc109-4aaa-40e0-bdcc-7039d31533f8 +deleted:false +working:true +live:true +languageId:1 /orderBy/modDate desc/limit/0",
        timeout=60 * 5,
    )
    return r.json()["contentlets"]


def write_to_file(code_to_title, title_to_code):
    """Writes mappings to JSON file"""

    mappings = {
        "code_to_title": code_to_title,
        "title_to_code": title_to_code,
    }

    with open("data/utility/programCodeMappings.json", "w", encoding="utf8") as FILE:
        json.dump(mappings, FILE, indent=4)


if __name__ == "__main__":
    get_mappings()
