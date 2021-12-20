from algorithms.objects.categories import *
from algorithms.objects.conditions import *
from algorithms.objects.user import User
from algorithms.objects.helper import *


import re

def create_category(tokens):
    '''Given a list of tokens starting from after the connector keyword, create
    and return the category object matching the category, as well as the current index
    of the token list.'''

    # At most we will only parse 1 or 2 tokens so no need for an iterator
    # NOTE: There will always be at least 2 tokens due to a closing ")" bracket
    # so it is safe to check tokens[1]
    if re.match(r'^[A-Z]{4}$', tokens[0], flags=re.IGNORECASE):
        # Course type
        return CourseCategory(tokens[0]), 0
    elif re.match(r'^L[0-9]$', tokens[0], flags=re.IGNORECASE):
        # Level category. Get the level, then determine next token if there is one
        level = int(re.match(r'^L([0-9])$', tokens[0],
                    flags=re.IGNORECASE).group(1))

        if re.match(r'^[A-Z]{4}$', tokens[1], flags=re.IGNORECASE):
            # Level Course Category. e.g. L2 MATH
            course_code = re.match(r'^([A-Z]{4})$', tokens[1], flags=re.IGNORECASE).group(1)

            return LevelCourseCategory(level, course_code), 1
        else:
            # There are no tokens after this. Simple level category
            return LevelCategory(level), 0
    elif re.match(r'^S$', tokens[0], flags = re.IGNORECASE):
         # School category
         return SchoolCategory(f"{tokens[0]} {tokens[1]}"), 1
    elif re.match(r'^F$', tokens[0], flags=re.IGNORECASE):
         # Faculty category
         return FacultyCategory(f"{tokens[0]} {tokens[1]}"), 1

    # TODO: Levels (e.g. SPECIALISATIONS, PROGRAM)

    # Did not match any category. Return None and assume only 1 token was consumed
    return None, 0


def create_condition(tokens, course=None):
    '''
    The main wrapper for make_condition so we don't get 2 returns.
    Given the parsed logical tokens list (assuming starting and ending bracket),
    and optionally a course for which this condition applies to,
    Returns the condition
    '''
    return make_condition(tokens, True, course)[0]

def make_condition(tokens, first=False, course=None):
    '''
    To be called by create_condition
    Given the parsed logical tokens list, (assuming starting and ending bracket),
    return the condition object and the index of that (sub) token list
    '''

    # Everything is wrapped in a CompositeCondition
    if first == True:
        result = FirstCompositeCondition(course=course)
    else:
        result = CompositeCondition()

    it = enumerate(tokens)
    for index, token in it:
        if token == '(':
            # Parse content in bracket 1 layer deeper
            sub_result, sub_index = make_condition(tokens[index + 1:])
            if sub_result == None:
                # Error. Return None
                return None, sub_index
            else:
                # Adjust the cur/rent position to scan the next token after this sub result
                result.add_condition(sub_result)
                [next(it) for _ in range(sub_index + 1)]
        elif token == ')':
            # End parsing and go up one layer
            return result, index
        elif token == "&&":
            # AND type logic
            result.set_logic(AND)
        elif token == "||":
            # OR type logic
            result.set_logic(OR)
        elif token == "[":
            # Beginning of co-requisite. Parse courses and logical operators until closing "]"
            coreq_cond = CoreqCoursesCondition()
            
            i = 1 # Helps track our index offset to parse this co-requisite
            while tokens[index + i] != "]":
                if is_course(tokens[index + i]):
                    coreq_cond.add_course(tokens[index + i])
                elif tokens[index + i] == "&&":
                    coreq_cond.set_logic(AND)
                elif tokens[index + i] == "||":
                    coreq_cond.set_logic(OR)
                else:
                    # Error, bad token processed. Return None
                    return None, index + i
                i += 1
                next(it)
            
            result.add_condition(coreq_cond)

            # Skip the closing "]" so the iterator will continue with the next token
            next(it)
        elif is_course(token):
            # Condition for a single course
            result.add_condition(CourseCondition(token))
        elif is_uoc(token):
            # Condition for UOC requirement
            uoc = get_uoc(token)
            uoc_cond = UOCCondition(uoc)

            if tokens[index + 1] == "in":
                # Create category according to the token after 'in'
                next(it)  # Skip "in" keyword

                # Get the category of the uoc condition
                category, sub_index = create_category(tokens[index + 2:])

                if category == None:
                    # Error. Return None. (Could also potentially set the uoc category
                    # to just the default Category which returns true and 1000 uoc taken)
                    return None, index
                else:
                    # Add the category to the uoc and adjust the current index position
                    uoc_cond.set_category(category)
                    [next(it) for _ in range(sub_index + 1)]

            result.add_condition(uoc_cond)
        elif is_wam(token):
            # Condition for WAM requirement
            wam = get_wam(token)
            wam_cond = WAMCondition(wam)

            if tokens[index + 1] == "in":
                # Create category according to the token after 'in'
                next(it)  # Skip "in" keyword
                category, sub_index = create_category(tokens[index + 2:])

                if category == None:
                    # If can't parse the category, return None(raise an error)
                    return None, index
                else:
                    # Add the category and adjust the current index position
                    wam_cond.set_category(category)
                    [next(it) for _ in range(sub_index + 1)]

            result.add_condition(wam_cond)
        elif is_grade(token):
            # Condition for GRADE requirement (mark in a single course)
            grade = get_grade(token)

            if tokens[index + 1] == "in":
                # Next token is "in" or else there has been an error
                next(it)  # Skip "in" keyword and course code
                next(it)

                result.add_condition(GRADECondition(grade, tokens[index + 2]))

                # NOTE: Don't need to create a category since I think grade ONLY applies to coursecode
                # grade_category, sub_index = create_category(tokens[index + 2:])
                # categories.append(grade_category)
            else:
                # Error
                return None, index
        elif is_program(token):
            result.add_condition(ProgramCondition(token))
        elif is_specialisation(token):
            result.add_condition(SpecialisationCondition(token))
        else:
            # Unmatched token. Error
            return None, index

    return result, index