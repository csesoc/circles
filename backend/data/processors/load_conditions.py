"""
Will pickle all the conditions into a dictionary. Run this file from the backend
folder with python3 -m algorithms.load_conditions
"""

import pickle

from algorithms.create import create_condition
from algorithms.objects.conditions import CompositeCondition
from algorithms.objects.helper import read_data
from data.config import CONDITIONS_PICKLE_FILE, CONDITIONS_TOKEN_FILE


def construct_conditions_objects() -> dict[str, CompositeCondition | None]:
    """
    Construct conditions objects by reading all conditions tokens
    and then creating a condition object for each course.

    Returns: {
            "CODEXXX" (str) : <CompositeCondition>
        }
    """
    # Load all the conditions objects
    all_conditions_tokens = read_data(CONDITIONS_TOKEN_FILE)

    # Create a dictionary of all the conditions objects
    all_objects: dict[str, CompositeCondition | None] = {}
    for course, tokens in all_conditions_tokens.items():
        all_objects[course] = create_condition(tokens, course)
    return all_objects

def cache_conditions_pkl_file():
    """
    Loads all conditions objects and dumps them as a pickled file

    Input: None
    Returns: None
    """
    all_objects: dict[str, CompositeCondition | None] = construct_conditions_objects()

    # Dump the dictionary as a pickle file
    with open(CONDITIONS_PICKLE_FILE, "wb") as f_out:
        pickle.dump(all_objects, f_out, pickle.HIGHEST_PROTOCOL)


def main() -> None:
    """ main """
    cache_conditions_pkl_file()

if __name__ == "__main__":
    main()
