"""
Program extracts raw data for Programs and place data in file
'programsRaw.json', ready for formatting.

Step in the data's journey:
    [ X ] Scrape raw data (programScraper.py)
    [   ] Format scraped data (programFormatting.py)
    [   ] Customise formatted data (programProcessing.py)
"""

from data.scrapers.payload import do_requests
from data.utility import data_helpers

TOTAL_PGRMS = 700 # slighly less than this


def scrape_prg_data():
    """
    Retrieves data for all undergraduate programs
    """
    data = do_requests("course", items_per_req=20, max_items=TOTAL_PGRMS)

    # we are only keeping undergrad ones for now
    data = [obj for obj in data if obj["studyLevelValue"] == "ugrd"]

    data_helpers.write_data(
        data, "data/scrapers/programsPureRaw.json"
    )


if __name__ == "__main__":
    scrape_prg_data()
