""" an autoplanning solver which takes in courses and spits a plan """
from pprint import pprint
from typing import Tuple

from algorithms.objects.course import Course
from algorithms.objects.user import User
from ortools.sat.python import cp_model  # type: ignore
from server.routers.model import CONDITIONS

# Inspired by AbdallahS's code here: https://github.com/AbdallahS/planner
# with help from Martin and MJ :)

def terms_between(start: Tuple[int, int], end: Tuple[int, int]):
    return (end[0] - start[0]) * 4 + end[1] - start[1]

def map_var_to_course(courses: list[Course], var: cp_model.IntVar):
    return [course for course in courses if course.name == var.Name()][0]

def map_course_to_var(course: Course, variables: list[cp_model.IntVar]):
    return [variable for variable in variables if course.name == variable.Name()][0]

def convert_to_term_year(number: int, start: Tuple[int, int]):
    return (number // 4 + start[0], number % 4 + start[1])

def autoplan(courses: list[Course], user: User, start: Tuple[int, int], end: Tuple[int, int], uoc_max: list[int]) -> list[Tuple[str, Tuple[int, int]]]:
    """
    given a list of courses, we will fill our terms in a valid ordering.
    we will enforce that:
        - the course must be offered in that term
        - duplicate courses (usually only multiterm courses) must be taken consecutively
        - the UOC max for each term is adhered to (no overloading, and the user should be allowed to manipulate this)
        - the prerequisites are respected.
    """
    # pylint: disable=too-many-locals
    # TODO: add a way to lock in courses
    model = cp_model.CpModel()
    # 1. enforces terms
    variables = [model.NewIntVarFromDomain(cp_model.Domain.FromIntervals(course.term_domain(start, end)), course.name) for course in courses]
    # 2. if any courses are named the same, then they must be taken consecutively
    possible_course_dupes = [course.name for course in courses if not course.locked]
    duplicate_courses = set(c for c in possible_course_dupes if possible_course_dupes.count(c) > 1)
    for dupe in duplicate_courses:
        matched_courses = [variable for variable in variables if variable.Name() == dupe]
        for match, next_match in zip(matched_courses, matched_courses[1:]):
            model.Add(match + 1 == next_match)

    # 3. set max UOC for a term
    for index, m in enumerate(uoc_max):
        boolean_indexes = []
        for v in variables:
            # b is a 'channeling constraint'. This is done to fill the resovoir only *if* the course is in that given term
            # https://developers.google.com/optimization/cp/channeling
            b = model.NewBoolVar('hi')
            model.Add(v == index).OnlyEnforceIf(b)
            model.Add(v != index).OnlyEnforceIf(b.Not())
            boolean_indexes.append(b)
        # if the course is in term 'index', only allow 0 to m UOC to exist in that term.
        model.AddReservoirConstraintWithActive(
            variables,
            list(map_var_to_course(courses, var).uoc for var in variables),  # this fills the resovoir by UoC units if active
            boolean_indexes,  # a course is only active if in term 'index'
            0,
            m  # uoc_max
        )

    # 4. enforce prereqs, only if not locked by user
    for course in courses:
        if course.locked:
            continue

        # this is the responsibility of the condition class to generate prereq model.
        course.condition.condition_to_model(
            model,
            user,
            list((variable, map_var_to_course(courses, variable)) for variable in variables),
            map_course_to_var(course, variables)
        )
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in [cp_model.MODEL_INVALID, cp_model.INFEASIBLE]:
        raise ValueError(f'your courses are impossible to put in these terms! Error code: {status}')
    return [(v.Name(), convert_to_term_year(solver.Value(v), start)) for v in variables]


if __name__ == '__main__':
    pprint(autoplan(
        [
            Course("MATH1141", CONDITIONS["MATH1141"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("MATH1081", CONDITIONS["MATH1081"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP1511", CONDITIONS["COMP1511"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP2521", CONDITIONS["COMP2521"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("COMP2041", CONDITIONS["COMP2041"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP1531", CONDITIONS["COMP1531"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("COMP1521", CONDITIONS["COMP1521"], 65, 6, {2020: [1, 2], 2021: [1, 2], 2022: [1, 2]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 65, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 65, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 65, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP2511", CONDITIONS["COMP2511"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH1241", CONDITIONS["MATH1141"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH3411", CONDITIONS["MATH3411"], 65, 6, {2020: [3], 2021: [3], 2022: [3]}),
            Course("COMP3411", CONDITIONS["COMP3411"], 65, 6, {2020: [3], 2021: [0], 2022: [0]}),
            Course("COMP6841", CONDITIONS["COMP6841"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3231", CONDITIONS["COMP3231"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3141", CONDITIONS["COMP3141"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP3121", CONDITIONS["COMP3121"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("COMP3131", CONDITIONS["COMP3131"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP4141", CONDITIONS["COMP4141"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3311", CONDITIONS["COMP3311"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ARTS1360", CONDITIONS["ARTS1360"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
        ],
        User({
            "program": "3778",
            "specialisations" : ["COMPA1"],
            "courses": {}
        }),
        (2020, 0),
        (2023, 3),
        [12, 20, 20, 20, 12, 20, 20, 20, 10, 20, 20, 20]
    ))
