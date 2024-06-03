"""
Program extracts raw data for specialisations and place data in file
'specialisationsPureRaw.json', ready for formatting.

Step in the data's journey:
    [ X ] Scrape raw data (specialisationsScraper.py)
    [   ] Format scraped data (specialisationFormatting.py)
    [   ] Customise formatted data (specialisationProcessing.py)
"""

import json

import requests
from data.scrapers.payload import HEADERS, URL, do_requests
from data.utility import data_helpers

# Note as at May 2021, there are 365 specialisations
TOTAL_SPNS = 2000


def scrape_spn_data():
    """Retrieves data for all undergraduate specialisations"""

    data = do_requests("aos", items_per_req=20, max_items=TOTAL_SPNS )

    data_helpers.write_data(
        data, "data/scrapers/specialisationsPureRaw.json"
    )


if __name__ == "__main__":
    scrape_spn_data()
