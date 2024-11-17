import re
import sys

from data.utility import data_helpers

CONDITIONS = data_helpers.read_data("data/final_data/conditionsProcessed.json")

KNOWN_WORDS = {"&&", "||", "in"}

PROCESSED = "processed"

# Conditions that have had manual fixes applied
FINAL_CONDITIONS = ["ACCT", "COMP"]


def parse_syntax():

    res = input(
        "Type 'y' to print errors to file syntaxErrors.txt or any other key for stdout: "
    )

    orig_stdout = sys.stdout
    if res == "y":
        with open("syntaxErrors.txt", "w", encoding="utf8") as f:
            sys.stdout = f

    for course, condition in CONDITIONS.items():

        if course[:4] not in FINAL_CONDITIONS:
            continue

        if not do_brackets_match(condition[PROCESSED]):
            print("Failed bracket match!")
            print(f"{course}: {condition[PROCESSED]}\n")

        unknown = find_unknown_words(condition[PROCESSED])
        if unknown:
            print("Unknown word(s) in condition")
            print(f"{course}: {condition[PROCESSED]}")
            print(f"Unknown: {unknown}\n")

    sys.stdout = orig_stdout


def find_unknown_words(processed):
    """
    Checks whether words in processed condition are known to the algorithm.
    Returns a list of all unknown words.
    """
    unknown = []
    words = processed.split(" ")

    for word in words:
        # Remove formatting
        word = re.sub(r"[,.\)\(\[\]]", "", word)
        if re.match(r"^[A-Z]{4,5}\d{0,5}$", word):
            # Ignore course codes: e.g. COMP, COMP1511, ACTB13554
            continue
        if re.match(r"^[A-Z]{4}\??(1|2|H|#)$", word):
            # Ignore mapping codes: e.g. COMP?1, COMP#
            continue
        if re.match(r"^\d{4}$", word):
            # Ignore program codes
            continue
        if re.match(r"^\d{1,3}(WAM|UOC|GRADE)$", word):
            # Ignore WAM, GRADE, and UOC words
            continue

        if word and word not in KNOWN_WORDS:
            unknown.append(word)

    return unknown


def do_brackets_match(processed):
    """
    Checks whether brackets are valid and matching.
    """

    bracket_map = {"(": ")", "[": "]"}
    closing = {")", "]"}
    stack = []

    for char in processed:

        if char in bracket_map:
            # Opening brackets
            stack.append(char)

        elif char in closing:
            # Closing brackets
            if len(stack) == 0:
                return False

            popped = stack.pop()
            if char != bracket_map[popped]:
                return False

    if len(stack) != 0:
        # Stack should be empty in the end
        return False

    return True


if __name__ == "__main__":
    parse_syntax()
