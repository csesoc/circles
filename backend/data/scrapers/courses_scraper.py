"""
Program extracts raw data for Programs and place data in file
'coursesPureRaw.json', ready for formatting.

Step in the data's journey:
    [ X ] Scrape raw data (coursesScraper.py)
    [   ] Format scraped data (coursesFormatting.py)
    [   ] Customise formatted data (coursesProcessing.py)
"""


from data.scrapers.payload import do_requests
from data.utility import data_helpers

TOTAL_COURSES = 10000


def scrape_course_data(year = None):
    """
    Retrieves data for all undergraduate courses
    Makes the request to the handbook, scrape the data and calls
    write_data to dump the json to an OUTPUT_FILE
    """

    data = do_requests("subject", items_per_req=100, max_items=TOTAL_COURSES)

    # for now, filter courses to get only undergrad (remove later)
    data = [obj for obj in data if obj["studyLevelValue"] == "ugrd"]

    data_helpers.write_data(
        data,
        "data/scrapers/coursesPureRaw.json"
        if year is None else
        f"data/final_data/archive/raw/{year}.json"
    )


if __name__ == "__main__":
    scrape_course_data()
