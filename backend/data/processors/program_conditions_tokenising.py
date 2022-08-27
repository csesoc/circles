"""
DOCUMENTATION: TBA

This file currently does the job of two. TODO: move stuff out

1. Pre-process condition tokenisations
2. Tokenise conditions


"""


import re
from typing import Dict, List

from data.utility.data_helpers import read_data, write_data

PROGRAMS_PROCESSED_PATH = "data/processed/programsProcessed.json"
PRE_PROCESSED_DATA_PATH = "data/final_data/programsConditionsPreProcessed.json"
FINAL_TOKENS_PATH = "data/final_data/programsConditionsTokens.json"

def pre_process_program_requirements(program_info: Dict) -> List[Dict]:
    """
    Recieves the relevant information from a course from `programsProcessed.json`
    and applies pre-processing requirements so that it can be tokenised.

    As a sanity check there are ~40 instances of programs with such requirements.

    The relevant conditions live inside `non_spec_data` section of a program
    """
    non_spec_data: List[Dict] = program_info.get("componenents", {}).get("non_spec_data", [])
    if not len(non_spec_data):
        return {}
    return [
        pre_process_cond(condition) for condition in non_spec_data
        if condition is not None
    ]

def pre_process_cond(condition: Dict):
    """
    Takes a raw condition and pre-processes it.
    The condition will be a dict with atleast the following keys:
        - "type"
        - "title"
        - "notes"
    We care for instances where the type is "info_rule". The rest relates to items such as core courses, etc.
    The relevant information about maturity and other rules is usually inside the "notes" field.
    Though typically the "title" will clarify that there is a maturity requirement, it is not a guarantee
    as  it may be of form "Program Rules and Dictionary"
    """
    if not condition.get("type", None) == "info_rule":
        return None
    if not is_relevant_string(condition.get("notes", "")) and not is_relevant_string(condition.get("title", "")):
        return None
    # Epic regex happens here
    # Remove all cringe stuff

def is_relevant_string(string: str) -> bool:
    """
    Checks if a string is relevant to the tokenisation process.
    """
    return bool(
        re.search(r"*maturity*", string)
    )

def tokenise_program_requirements(program_info: Dict) -> Dict:
    """
    Recieves the pre-processed program info and tokenises the conditions.
    """
    return program_info

def main():
    program_info = read_data()

    pre_processed: Dict = {}
    for code, info in program_info.items():
        pre_processed[code] = pre_process_program_requirements(info)
    write_data(pre_processed)

    final: Dict = {}
    for code, info in pre_processed.items():
        final[code] = tokenise_program_requirements(info)

    write_data(final)

main()


