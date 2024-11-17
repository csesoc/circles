"""
route for planner algorithms
"""

from math import lcm
from operator import itemgetter
from typing import Annotated, Dict, List

from algorithms.autoplanning import autoplan
from algorithms.transcript import parse_transcript
from algorithms.validate_term_planner import validate_terms
from fastapi import APIRouter, HTTPException, Security, UploadFile
from server.routers.utility.sessions.middleware import HTTPBearerToUserID
from server.routers.utility.user import get_setup_user, set_user, user_storage_to_algo_user, user_storage_to_raw_plan
from server.routers.model import CourseCode, CoursesState, PlannedToTerm, ProgramTime, UnPlannedToTerm
from server.routers.utility.common import get_course_details, get_course_object

MIN_COMPLETED_COURSE_UOC = 6


router = APIRouter(
    prefix="/planner", tags=["planner"], responses={404: {"description": "Not found"}}
)

require_uid = HTTPBearerToUserID()

@router.get("/")
def planner_index() -> str:
    """ sanity test that this file is loaded """
    return "Index of planner"


@router.get("/validateTermPlanner", response_model=CoursesState)
def validate_term_planner(uid: Annotated[str, Security(require_uid)]) -> CoursesState:
    """
    Will iteratively go through the term planner data whilst
    iteratively filling the user with courses.

    Returns the state of all the courses on the term planner
    """
    user = get_setup_user(uid)
    courses_state = validate_terms(
        programCode=user['degree']['programCode'],
        specs=user['degree']['specs'],
        plan=user_storage_to_raw_plan(user)
    )
    return CoursesState(courses_state=courses_state)


@router.post("/addToUnplanned")
def add_to_unplanned(data: CourseCode, uid: Annotated[str, Security(require_uid)]):
    """
    Adds a course to the user's unplanned column within their planner

    Args:
        data (CourseCode):
            - courseCode(str): The course to add to the unplanned column
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.
    """
    user = get_setup_user(uid)
    if data.courseCode in user['courses'].keys() or data.courseCode in user['planner']['unplanned']:
        raise HTTPException(status_code=400, detail=f'{data.courseCode} is already planned.')

    uoc = get_course_details(data.courseCode)['UOC'] # raises exception anyway when unfound
    user['planner']['unplanned'].append(data.courseCode)
    user['courses'][data.courseCode] = {
        'code': data.courseCode,
        'mark': None,
        'uoc': uoc,
        'ignoreFromProgression': False
    }
    set_user(uid, user, True)


@router.post("/unPlannedToTerm")
def set_unplanned_course_to_term(data: UnPlannedToTerm, uid: Annotated[str, Security(require_uid)]):
    """
    Moved a course out of the user's unplanned column and into the specified course on their planner

    Args:
        data (UnPlannedToTerm):
            - destRow(int): The row in the planner the course should be moved to
            - destTerm(str): The term in the planner the course should be moved to
            - destIndex(int): The index within the term the course should be moved to
                (incase there are multiple courses in the same term)
            - courseCode(str): The course to add to the unplanned column
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.

    Raises:
        HTTPException: Moving a multiterm course somewhere that would result in a
            course being placed before or after the planner
    """
    course = get_course_details(data.courseCode)
    uoc, terms = itemgetter('UOC', 'terms')(course)
    user = get_setup_user(uid)
    planner = user['planner']
    instance_num = 0
    terms_list = get_terms_list(
        data.destTerm, uoc, terms, planner['isSummerEnabled'], instance_num)

    # If moving a multiterm course out of bounds
    if course['is_multiterm'] and out_of_bounds(len(planner['years']), data.destRow, terms_list):
        raise HTTPException(status_code=400,
                            detail=f'{data.courseCode} would extend outside of the term planner. \
                Either drag it to a different term, or extend the planner first')
    planner['unplanned'].remove(data.courseCode)

    # If multiterm add multiple instances of course
    if course['is_multiterm']:
        terms_list.pop(instance_num)
        planner['years'][data.destRow][data.destTerm].insert(
            data.destIndex, data.courseCode)
        for term_row in terms_list:
            term, row_offset = itemgetter('term', 'row_offset')(term_row)
            index = len(planner['years'][data.destRow + row_offset][term])
            planner['years'][data.destRow +
                             row_offset][term].insert(index, data.courseCode)
    else:
        planner['years'][data.destRow][data.destTerm].insert(
            data.destIndex, data.courseCode)
    set_user(uid, user, True)


@router.post("/plannedToTerm")
def set_planned_course_to_term(data: PlannedToTerm, uid: Annotated[str, Security(require_uid)]):
    """
    Moves a course out of one term and into a second term.

    Args:
        data (PlannedToTerm):
            - srcRow(int): The row in the planner the course was originally in
            - srcTerm(str): The term in the planner the course was originally in
            - destRow(int): The row in the planner the course should be moved to
            - destTerm(str): The term in the planner the course should be moved to
            - destIndex(int): The index within the term the course should be moved to
                (incase there are multiple courses in the same term)
            - courseCode(str): The course to add to the unplanned column

        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.

    Raises:
        HTTPException: Moving a multiterm course somewhere that would result in a
            course being placed before or after the planner
    """
    # pylint: disable=too-many-locals
    course = get_course_details(data.courseCode)
    user = get_setup_user(uid)

    uoc, terms_offered, is_multiterm = itemgetter(
        'UOC', 'terms', 'is_multiterm')(course)

    src_term_list = []

    # If only changing index of multiterm course, don't change other course instances
    if is_multiterm and data.srcRow == data.destRow and data.srcTerm == data.destTerm:
        user['planner']['years'][data.srcRow][data.srcTerm].remove(
            data.courseCode)
        user['planner']['years'][data.srcRow][data.srcTerm].insert(
            data.destIndex, data.courseCode)
        set_user(uid, user, True)
        return

    # Remove every instance of the course from the planner
    previous_index = {}
    for year in range(len(user['planner']['years'])):
        terms = user['planner']['years'][year]
        for term in terms:
            target_term: list = user['planner']['years'][year][term]
            try:
                course_index = target_term.index(data.courseCode)
            except ValueError:
                course_index = None
            if course_index is not None:
                previous_index[f'{year}{term}'] = course_index
                target_term.remove(data.courseCode)
                src_term_list.append(term)

    instance_num = src_term_list.index(data.srcTerm)
    new_terms = get_terms_list(
        data.destTerm,
        uoc,
        terms_offered,
        user['planner']['isSummerEnabled'],
        instance_num
    ) if is_multiterm else []

    # If multiterm course and out of bounds, raise exception without updating database
    if is_multiterm and out_of_bounds(len(user['planner']['years']), data.destRow, new_terms):
        raise HTTPException(status_code=400,
                            detail=f'{data.courseCode} would extend outside of the term planner. \
                Either drag it to a different term, or extend the planner first')
    if is_multiterm:
        new_terms.pop(instance_num)

    first_term = user['planner']['years'][data.destRow][data.destTerm]
    drop_index = data.destIndex

    # If dragged multiterm course to a column it already exists in
    if is_multiterm and f'{data.destRow}{data.destIndex}' in previous_index:
        curr_index = previous_index[f'{data.destRow}{data.destIndex}']
        if curr_index < data.destIndex:
            drop_index -= 1

    # Move every instance of course
    first_term.insert(drop_index, data.courseCode)
    for term_row_offset in new_terms:
        term, row_offset = itemgetter('term', 'row_offset')(term_row_offset)
        target_term = user['planner']['years'][data.destRow + row_offset][term]
        term_id = f'{data.destRow + row_offset}{term}'
        index = previous_index[term_id] if term_id in previous_index else len(
            target_term)
        target_term.insert(index, data.courseCode)
    set_user(uid, user, True)


@router.post('/removeCourse')
def remove_course(data: CourseCode, uid: Annotated[str, Security(require_uid)]):
    """
    Removes a course from the user's planner data

    Args:
        data (CourseCode):
            - courseCode(str): The course to add to the unplanned column
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.
    """
    user = get_setup_user(uid)
    planner = user['planner']

    # remove course from years (if it's there)
    for year in planner['years']:
        for _, course_list in year.items():
            if data.courseCode in course_list:
                course_list.remove(data.courseCode)

    # remove course from unplanned (if it's there)
    if data.courseCode in planner['unplanned']:
        planner['unplanned'].remove(data.courseCode)

    if data.courseCode in user['courses']:
        del user['courses'][data.courseCode]
    set_user(uid, user, True)

@router.post('/toggleIgnoreFromProgression')
def toggle_ignore_from_progression(data: CourseCode, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['courses'][data.courseCode]['ignoreFromProgression'] = not user['courses'][data.courseCode]['ignoreFromProgression']
    set_user(uid, user, True)


@router.post("/removeAll")
def remove_all(uid: Annotated[str, Security(require_uid)]):
    """
    Removes all courses from the user's planner data

    Args:
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.
    """
    user = get_setup_user(uid)

    # Replace each year with an empty year
    user['planner']['years'] = generate_empty_years(len(user['planner']))

    # Clear unplanned column
    user['planner']['unplanned'] = []

    user['courses'] = {}
    set_user(uid, user, True)


@router.post("/unscheduleCourse")  # TODO: What if someone is enrolled in the same couse twice?
def unschedule(data: CourseCode, uid: Annotated[str, Security(require_uid)]):
    """
    Moves a course out of a term and into the user's unplanned column

    Args:
        data (CourseCode):
            - courseCode(str): The course to add to the unplanned column
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.
    """
    user = get_setup_user(uid)

    # Remove every instance of the course from each year and add to unplanned
    removed = False
    for year in user['planner']['years']:
        for course_list in year.values():
            if data.courseCode in course_list:
                removed = True
                course_list.remove(data.courseCode)
                user['planner']['unplanned'].append(data.courseCode)

    if not removed:
        raise HTTPException(status_code=400, detail=f'{data.courseCode} not found in planner')

    set_user(uid, user, True)


@router.post('/unscheduleAll')
def unschedule_all(uid: Annotated[str, Security(require_uid)]):
    """
    Removes all courses from every term and moves then into the user's unplanned column.

    Args:
        token (str, optional): The user's authentication token. Defaults to DUMMY_TOKEN.
    """
    user = get_setup_user(uid)

    # Remove every course from each term and add it to unplanned
    for year in user['planner']['years']:
        for course_list in year.values():
            user['planner']['unplanned'].extend(course_list)
            course_list.clear()

    set_user(uid, user, True)

@router.post("/toggleTermLocked")
def toggleLocked(termyear: str, uid: Annotated[str, Security(require_uid)]):
    (year_str, term_str) = termyear.split('T')
    if not (term_str.isnumeric() and year_str.isnumeric() and 0 <= int(term_str) <= 3):
        raise HTTPException(status_code=400, detail="Invalid term/year")

    user = get_setup_user(uid)
    locked_map = user['planner']['lockedTerms']
    locked_map[termyear] = not locked_map.get(termyear, False)
    set_user(uid, user, True)

@router.post('/addFromTranscript')
def add_from_transcript(file: UploadFile, uid: Annotated[str, Security(require_uid)]):
    """
    Adds all courses from a transcript into a user's courses
    """
    user = get_setup_user(uid)
    transcript_obj = parse_transcript(file.file)

    # pad start with more years
    savedStartYear = user['planner']['startYear']
    transStartYear = min(transcript_obj)
    if savedStartYear > transStartYear:
        user['planner']['years'] = generate_empty_years(savedStartYear - transStartYear) + user['planner']['years']
        user['planner']['startYear'] = transStartYear

    # pad end with more years
    transEndYear = max(transcript_obj)
    if transEndYear > user['planner']['startYear'] + len(user['planner']['years']) - 1:
        user['planner']['years'] += generate_empty_years(transEndYear - user['planner']['startYear'] - len(user['planner']['years']) + 1)

    for year, terms_obj in transcript_obj.items():
        year_offset = year - user['planner']['startYear']
        year_data = user['planner']['years'][year_offset]
        for term, courses_obj in terms_obj.items():
            for course, (uoc, mark, _) in courses_obj.items():
                year_data[term].append(course)
                user['courses'][course] = {
                    'code': course,
                    'mark': mark,
                    'uoc': uoc or 6, # guess normal uoc
                    'ignoreFromProgression': False
                }

    set_user(uid, user, True)


def generate_empty_years(num_years: int):
    """
    Generates a set amount of empty years

    Args:
        num_years (int): Number of empty year to create

    Returns:
        List[List[terms]]: An empty list of years and terms
    """
    return [{'T0': [], 'T1': [], 'T2': [], 'T3': []} for _ in range(num_years)]


def get_terms_list(
    current_term: str,
    uoc: int,
    terms_offered: list[str],
    is_summer_enabled: bool,
    instance_num: int
):
    """
    Determines which terms a multiterm course should be moved to.
    Some multiterm courses need to be done 2 times, whereas others need to be
    done 3 times, so it can't be hard-coded

    Args:
        current_term (str): The term the multi-term course is being moved to
        uoc (int): The UOC each instance of the course counts as
        terms_offered (list[str]): A list of terms the course is offered in
        is_summer_enabled (bool): Whether multiterm courses can go in the summer term
        instance_num (int): Which instance of the multiterm course is being dragged

    Returns:
        List[Dict[str, str | int]]: A list of terms and their offsets from the original
            row that the multiterm course will be moved to
    """
    all_terms = ['T1', 'T2', 'T3']
    terms_list: List[Dict[str, int | str]] = []
    if is_summer_enabled:
        all_terms.insert(0, 'T0')

    # Remove any unavailable terms
    terms = sorted(list(set(all_terms) & set(terms_offered)))
    try:
        index = terms.index(current_term) - 1
    except ValueError:
        return []
    row_offset = 0

    num_terms = lcm(uoc, MIN_COMPLETED_COURSE_UOC) // uoc

    for _ in range(instance_num):
        if index < 0:
            index = len(terms) - 1
            row_offset -= 1

        terms_list.insert(0, {
            'term': terms[(index + len(terms) % 3)],
            'row_offset': row_offset
        })

        index -= 1

    row_offset = 0
    index = terms.index(current_term)

    for _ in range(instance_num, num_terms):
        if index == len(terms):
            index = 0
            row_offset += 1

        terms_list.append({
            'term': terms[index],
            'row_offset': row_offset
        })

        index += 1
    return terms_list


def out_of_bounds(num_years, dest_row, terms):
    """
    Determines whether the result of get_terms will go out of bounds of the planner

    Args:
        num_years (int): The number of years in the planner
        dest_row (int): The row the multiterm course was placed in
        terms (List[Dict[str, str | int]]): The list of terms the multiterm
                                            course will go in if valid

    Returns:
        bool: Whether the multiterm course can be placed where specified
    """
    max_row_offset = max(terms, key=lambda x: x['row_offset'])['row_offset']
    min_row_offset = min(terms, key=lambda x: x['row_offset'])['row_offset']

    return dest_row + min_row_offset < 0 or dest_row + max_row_offset > num_years - 1


# TODO: Broken till migration is fixed; Previous planner methods are deprecated
# @router.post("/autoplanning/",
#              response_model=dict,
#              responses={
#                  400: {"description": "Bad Request e.g. can't create a plan with the given constraints`"},
#                  200: {
#                      "description": "Successful Response",
#                      "content": {
#                          "plan": [
#                              {
#                                  "T1": [
#                                      "COMP1511",
#                                      "MATH1131"
#                                  ],
#                                  "T3": [
#                                      "COMP1521"
#                                  ]
#                              },
#                              {
#                                  "T0": [
#                                      "COMP2521"
#                                  ],
#                                  "T2": [
#                                      "COMP1531"
#                                  ],
#                                  "T1": [
#                                      "COMP3821",
#                                      "COMP3891",
#                                  ]
#                              }
#                          ]
#                      }
#                  }
#              }
#              )
def autoplanning(uid: Annotated[str, Security(require_uid)], courseCodes: list[str], programTime: ProgramTime) -> dict:
    print("started to_user")
    user_data = get_setup_user(uid)
    user = user_storage_to_algo_user(user_data)
    print('finished the to_user')

    try:
        courses = [get_course_object(courseCode, programTime)
                   for courseCode in courseCodes]
        print('in the try')
        for year_index, year in enumerate(user_data['planner']['years']):
            for term_index in range(4):
                for course_code in year[f'T{term_index}']:
                    courses.append(
                        get_course_object(
                            course_code,
                            programTime,
                            (year_index, term_index),
                            user.get_grade(course_code)
                        )
                    )
        print("got to end")
        autoplanned = autoplan(
            courses, user, programTime.startTime, programTime.endTime, programTime.uocMax)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}") from e

    result: dict[str, list[dict]] = {"plan": [{} for _ in range(
        programTime.endTime[0] - programTime.startTime[0] + 1)]}

    for course, (year_autoplanned, term_autoplanned) in autoplanned:
        result["plan"][year_autoplanned - programTime.startTime[0]
                       ].setdefault(f'T{term_autoplanned}', []).append(course)
    return result
