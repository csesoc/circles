"""
DOCUMENTATION: https://github.com/csesoc/Circles/wiki/Tokenising-Conditions

Turns the processed conditions into a list, separated into logical blocks.
For example:
"COMP1511 || DPST1091 || COMP1911 || COMP1917"
==> [(, COMP1511, ||, DPST1091, ||, COMP1911, ||, COMP1917, )]

"65GRADE in COMP1927 || COMP2521"
==> [(, 65GRADE in COMP1927, ||, COMP2521, )]
"""

import re

from data.utility import data_helpers

PARSED_LOGIC: dict[str, list[str]] = {}

"""Converts the text condition into a json list"""


def tokenise_conditions():
    """
    Convert the processed conditions in conditionsProcessed.json into
    a list of string tokens, split on whitespaces and brackets/parenthesis.
    Add in logic and, write to conditionsTokens.json
    """
    data = data_helpers.read_data("data/final_data/conditionsProcessed.json")

    for code, condition in data.items():
        text = condition["processed"]

        # There are many words with (abcdefgh) where the brackets are attached
        # too tightly to the word. We first want to separate them like so:
        # ( abcdefgh ) so that our split can separate them cleanly.
        text = re.sub(r"\(", r" ( ", text)
        text = re.sub(r"\)", r" ) ", text)
        text = re.sub(r"\]", r" ] ", text)
        text = re.sub(r"\[", r" [ ", text)
        text = re.sub(r" +", r" ", text)

        logic = ["("]

        # Split on white space
        logic.extend(text.split())

        logic.append(")")

        PARSED_LOGIC[code] = logic

    data_helpers.write_data(PARSED_LOGIC, "data/final_data/conditionsTokens.json")
