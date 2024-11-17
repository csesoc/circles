"""
Configuration file for Data.

This is intended to be imported by modules executed from `/backend`.
Assumes that `/backend` is the current working directory.
"""
# NOTE: UNSW releases next year's handbook during the T2 holidays. However, it's
# assumed that circles will only stably update to this new handbook a few weeks
# into T3. In this case, all the students will have already locked in all their
# courses for the current year and thus, we can treat the current year as an
# archived year (saving us time from maintaining 2 sets of algorithms for the
# current AND the future year)

# The latest current handbook year that we will maintain all the algorithms for
from typing import List

# Don't forget to update live year in the frontend too
LIVE_YEAR: int = 2025

# The years for which we have archived
ARCHIVED_YEARS: List[int] = list(range(2019, LIVE_YEAR + 1))

# TODO: Consider adding file paths to this file so we don't have to type out
# the exact path to write to every time

CONDITIONS_TOKEN_FILE: str = "./data/final_data/conditionsTokens.json"
CONDITIONS_PICKLE_FILE: str = "./data/final_data/conditions.pkl"

GRAPH_CACHE_FILE = "./data/final_data/graph.json"
