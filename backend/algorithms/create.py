"""
This module allows for the conversion from strings / tokens of strings
to actual condition objects.
"""

import json
import re

from algorithms.objects.categories import (
    CourseCategory,
    FacultyCategory,
    LevelCategory,
    LevelCourseCategory,
    SchoolCategory,
)
from algorithms.objects.conditions import (
    CompositeCondition,
    CoreqCoursesCondition,
    CourseCondition,
    CourseExclusionCondition,
    GRADECondition,
    Logic,
    ProgramCondition,
    ProgramExclusionCondition,
    ProgramTypeCondition,
    SpecialisationCondition,
    UOCCondition,
    WAMCondition,
)
from algorithms.objects.helper import (
    get_grade,
    get_uoc,
    get_wam,
    is_course,
    is_grade,
    is_program,
    is_program_type,
    is_specialisation,
    is_uoc,
    is_wam,
)

# Load in cached exclusions
CACHED_EXCLUSIONS_PATH = "./algorithms/cache/exclusions.json"
with open(CACHED_EXCLUSIONS_PATH, "r", encoding="utf8") as f:
    CACHED_EXCLUSIONS = json.load(f)


def create_category(tokens):
    """Given a list of tokens starting from after the connector keyword, create
    and return the category object matching the category, as well as the current index
    of the token list.

    Returns:
        Category - Category object matching the category list
        int: The current index of the the token list
    """

    # At most we will only parse 1 or 2 tokens so no need for an iterator
    # NOTE: There will always be at least 2 tokens due to a closing ")" bracket
    # so it is safe to check tokens[1]
    if re.match(r"^[A-Z]{4}$", tokens[0], flags=re.IGNORECASE):
        # Course type
        return CourseCategory(tokens[0]), 0

    if re.match(r"^L[0-9]$", tokens[0], flags=re.IGNORECASE):
        # Level category. Get the level, then determine next token if there is one
        level = int(re.match(r"^L([0-9])$", tokens[0], flags=re.IGNORECASE).group(1))

        if re.match(r"^[A-Z]{4}$", tokens[1], flags=re.IGNORECASE):
            # Level Course Category. e.g. L2 MATH
            course_code = re.match(
                r"^([A-Z]{4})$", tokens[1], flags=re.IGNORECASE
            ).group(1)

            return LevelCourseCategory(level, course_code), 1

        # There are no tokens after this. Simple level category
        return LevelCategory(level), 0

    if re.match(r"^S$", tokens[0], flags=re.IGNORECASE):
        # School category
        return SchoolCategory(f"{tokens[0]} {tokens[1]}"), 1
    if re.match(r"^F$", tokens[0], flags=re.IGNORECASE):
        # Faculty category
        return FacultyCategory(f"{tokens[0]} {tokens[1]}"), 1

    # TODO Levels (e.g. SPECIALISATIONS, PROGRAM)

    # Did not match any category. Return None and assume only 1 token was consumed
    return None, 0


def create_condition(tokens, course=None):
    """
    The main wrapper for make_condition so we don't get 2 returns.
    Given the parsed logical tokens list (assuming starting and ending bracket),
    and optionally a course for which this condition applies to,
    Returns the condition
    """
    return make_condition(tokens, True, course)[0]


def make_condition(tokens, first=False, course=None):
    """
    To be called by create_condition
    Given the parsed logical tokens list, (assuming starting and ending bracket),
    return the condition object and the index of that (sub) token list

    Note:
    """
    # Everything is wrapped in a CompositeCondition
    result = CompositeCondition()
    # add exclusions
    if first and CACHED_EXCLUSIONS.get(course):
        # NOTE: we dont check for broken exclusions
        for exclusion in CACHED_EXCLUSIONS[course].keys():
            if is_course(exclusion):
                result.add_condition(CourseExclusionCondition(exclusion))
            elif is_program(exclusion):
                result.add_condition(ProgramExclusionCondition(exclusion))

    # Define index before loop to prevent undefined return
    index = 0
    item = enumerate(tokens)
    for index, token in item:
        if token == "(":
            # Parse content in bracket 1 layer deeper
            sub_result, sub_index = make_condition(tokens[index + 1 :])
            if sub_result is None:
                # Error. Return None
                return None, sub_index

            # Adjust the cur/rent position to scan the next token after this sub result
            result.add_condition(sub_result)
            [next(item) for _ in range(sub_index + 1)]
        elif token == ")":
            # End parsing and go up one layer
            return result, index
        elif token == "&&":
            # AND type logic
            result.set_logic(Logic.AND)
        elif token == "||":
            # OR type logic
            result.set_logic(Logic.OR)
        elif token == "[":
            # Beginning of co-requisite. Parse courses and logical
            # operators until closing "]"
            coreq_cond = CoreqCoursesCondition()
            i = 1  # Helps track our index offset to parse this co-requisite
            while tokens[index + i] != "]":
                if is_course(tokens[index + i]):
                    coreq_cond.add_course(tokens[index + i])
                elif tokens[index + i] == "&&":
                    coreq_cond.set_logic(Logic.AND)
                elif tokens[index + i] == "||":
                    coreq_cond.set_logic(Logic.OR)
                else:
                    # Error, bad token processed. Return None
                    return None, index + i
                i += 1
                next(item)

            result.add_condition(coreq_cond)

            # Skip the closing "]" so the iterator will continue with the next token
            next(item)
        elif is_course(token):
            # Condition for a single course
            result.add_condition(CourseCondition(token))
        elif is_uoc(token):
            # Condition for UOC requirement
            uoc = get_uoc(token)
            uoc_cond = UOCCondition(uoc)

            if index + 1 < len(tokens) and tokens[index + 1] == "in":
                # Create category according to the token after 'in'
                next(item)  # Skip "in" keyword

                # Get the category of the uoc condition
                category, sub_index = create_category(tokens[index + 2 :])

                if category is None:
                    # Error. Return None. (Could also potentially set the uoc category
                    # to just the default Category which returns true and 1000 uoc taken)
                    return None, index
                # Add the category to the uoc and adjust the current index position
                uoc_cond.set_category(category)
                [next(item) for _ in range(sub_index + 1)]

            result.add_condition(uoc_cond)

        elif is_wam(token):
            # Condition for WAM requirement
            wam_cond = WAMCondition(get_wam(token))

            if index + 1 < len(tokens) and tokens[index + 1] == "in":
                # Create category according to the token after 'in'
                next(item)  # Skip "in" keyword
                category, sub_index = create_category(tokens[index + 2 :])

                if category is None:
                    # If can't parse the category, return None(raise an error)
                    return None, index

                # Add the category and adjust the current index position
                wam_cond.set_category(category)
                [next(item) for _ in range(sub_index + 1)]

            result.add_condition(wam_cond)
        elif is_grade(token):
            # Condition for GRADE requirement (mark in a single course)
            grade = get_grade(token)

            if index + 1 < len(tokens) and tokens[index + 1] == "in":
                # Next token is "in" or else there has been an error
                next(item)  # Skip "in" keyword and course code
                next(item)

                result.add_condition(GRADECondition(grade, tokens[index + 2]))
            else:
                # Error
                return None, index
        elif is_program(token):
            result.add_condition(ProgramCondition(token))
        elif is_specialisation(token):
            result.add_condition(SpecialisationCondition(token))
        elif is_program_type(token):
            result.add_condition(ProgramTypeCondition(token))
        else:
            # Unmatched token. Error
            return None, index

    return result, index
