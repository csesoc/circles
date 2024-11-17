"""
The payload dict object is used by the course, program and specialisation
scraper and is (so far) the exact same between all three files, except
for the size of the payload. This module centralises creation of the payload
The module also defines the url and headers for the scrapers
"""



import json
import time

import requests
from data.config import LIVE_YEAR

URL = "https://api-ap-southeast-2.prod.courseloop.com/publisher/browsepage-academic-items?"
HEADERS = {
    "content-type": "application/json",
}
ITEMS_LIMIT = 20
REQ_DELAY = 0.1

def do_requests(content_type, items_per_req=ITEMS_LIMIT, max_items = 10000):
    """
    retuns a list of items.
    """
    offset = 0
    items_list = []
    while offset < max_items:
        data_payload = _create_payload(offset, items_per_req, content_type)
        r = requests.post(
            URL,
            data=json.dumps(data_payload),
            headers=HEADERS,
            timeout=60 * 5
        )
        # r.json() looks like { "data": { "data": [{}, ..., {}], "count": 123 } }
        print("brief output:", json.dumps(r.json())[:100], flush=True)
        cur_data = r.json()["data"]
        items_list.extend(cur_data["data"])
        offset += cur_data["count"]
        if cur_data["count"] == 0:
            break
        time.sleep(REQ_DELAY)
    return items_list

def _create_payload(offset, limit, content_type, year = LIVE_YEAR):
    """
    Create a payload of the given size
    content_type will be used as a prefix for the query fields
    Note: If changing any of the keys and passing them in as an argument,
    ensure that you add a default value for the argument so as to not
    break the payload for the other files
    """

    # Might get passed None as default value by the calling function
    if year is None:
        year = LIVE_YEAR

    return {
            "siteId": "unsw-prod-pres",
            "contentType": content_type,
            "queryParams": [{
                "queryField": "implementationYear",
                "queryValue": str(year)
            }],
            "offset": offset,
            "limit": limit
    }

def create_payload_gened(size, content_type, cl_id, academic_org, year : int | None =LIVE_YEAR):
    """
    Create a payload of the given size
    content_type will be used as a prefix for the query fields
    academic_org is either parentAcademicOrg or academicOrg depending on the faculty
    cl_id is the corresponding query string for academic_org
    Note: If changing any of the keys and passing them in as an argument,
    ensure that you add a default value for the argument so as to not
    break the payload for the other files
    """

    # Might get passed None as default value by the calling function
    if year is None:
        year = LIVE_YEAR

    return {
        "query":
            {"bool":
                {"filter": [{"terms": {"contenttype": [content_type]}},
                            {"term": {"live": True}}],
                    "must": [
                    {"query_string":
                        {"fields": [f"{content_type}.csTags"], "query":"*96d9bae4db2d4810fc9364e70596193a*"}},
                    {"query_string":
                        {"fields": [f"{content_type}.studyLevelValue"],
                         "query":"ugrd"}},
                    {"query_string":
                        {"fields": [f"{content_type}.implementationYear"],
                         "query":f"*{year}*"}}],
                    "must_not": [
                    {"query_string":
                        {"fields": [f"{content_type}.{academic_org}"], "query":cl_id}},

                    ]}},
        "sort": [{f"{content_type}.code_dotraw": "asc"}],
        "from": 0, "size": size,
    }
