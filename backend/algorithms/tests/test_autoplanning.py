from typing import Optional
from pytest import raises
from algorithms.autoplanning import autoplan, terms_between
from algorithms.objects.course import Course
from algorithms.objects.user import User
from algorithms.validate_term_planner import RawUserPlan, validate_terms
from pytest import raises
from server.routers.model import CONDITIONS


def get_uoc(course_name: str, courses: list[Course]):
    return [course.uoc for course in courses if course_name == course.name][0]

def get_mark(course_name: str, courses: list[Course]):
    return [course.mark for course in courses if course_name == course.name][0]

def test_basic_CS_autoplanning():
    assert_autoplanning_guarantees(
        [
            12, 20, 20, 20, 12, 20, 20, 20, 10, 20, 20, 20
        ],
        [
            Course("MATH1141", CONDITIONS["MATH1141"], 85, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("MATH1081", CONDITIONS["MATH1081"], 85, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP1511", CONDITIONS["COMP1511"], 85, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP2521", CONDITIONS["COMP2521"], 85, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("COMP2041", CONDITIONS["COMP2041"], 85, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP1531", CONDITIONS["COMP1531"], 85, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("COMP1521", CONDITIONS["COMP1521"], 85, 6, {2020: [1, 2], 2021: [1, 2], 2022: [1, 2]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 85, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 85, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ENGG2600", CONDITIONS["ENGG2600"], 85, 2, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP2511", CONDITIONS["COMP2511"], 85, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH1241", CONDITIONS["MATH1241"], 85, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH3411", CONDITIONS["MATH3411"], 85, 6, {2020: [3], 2021: [3], 2022: [3]}),
            Course("COMP3411", CONDITIONS["COMP3411"], 85, 6, {2020: [3], 2021: [0], 2022: [0]}),
            Course("COMP6841", CONDITIONS["COMP6841"], 85, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3231", CONDITIONS["COMP3231"], 85, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3141", CONDITIONS["COMP3141"], 85, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP3121", CONDITIONS["COMP3121"], 85, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("COMP3131", CONDITIONS["COMP3131"], 85, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP4141", CONDITIONS["COMP4141"], 85, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3901", CONDITIONS["COMP3901"], 85, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),  # cores conditions
            Course("ARTS1360", CONDITIONS["ARTS1360"], 85, 6, {2020: [2], 2021: [2], 2022: [2]}),
        ],
        "3778",
        ["COMPA1"]
    )

def test_more_complex_prereqs():
    # pick courses with cancerous prereqs and check that it all makes sense
    assert_autoplanning_guarantees(
        [
            12, 20, 20, 20, 12, 20, 20, 20, 10, 20, 20, 20
        ],
        [
            Course("MATH1141", CONDITIONS["MATH1141"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("MATH1081", CONDITIONS["MATH1081"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),  # coreq
            Course("COMP1511", CONDITIONS["COMP1511"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("COMP2521", CONDITIONS["COMP2521"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("COMP2041", CONDITIONS["COMP2041"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP1531", CONDITIONS["COMP1531"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("COMP1521", CONDITIONS["COMP1521"], 65, 6, {2020: [1, 2], 2021: [1, 2], 2022: [1, 2]}),
            Course("DESN1000", CONDITIONS["DESN1000"], 65, 2, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),
            Course("DESN2000", CONDITIONS["DESN2000"], 65, 2, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),  # terribly messy course prereq
            Course("COMP2511", CONDITIONS["COMP2511"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH1241", CONDITIONS["MATH1241"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),
            Course("MATH3411", CONDITIONS["MATH3411"], 65, 6, {2020: [3], 2021: [3], 2022: [3]}),
            Course("COMP3411", CONDITIONS["COMP3411"], 65, 6, {2020: [3], 2021: [0], 2022: [0]}),
            Course("COMP6441", CONDITIONS["COMP6441"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),  # maturity requirement course
            Course("COMP3231", CONDITIONS["COMP3231"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP3141", CONDITIONS["COMP3141"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
            Course("COMP3821", CONDITIONS["COMP3821"], 65, 6, {2020: [2, 3], 2021: [2, 3], 2022: [2, 3]}),  # mark requirement
            Course("COMP3131", CONDITIONS["COMP3131"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),
            Course("COMP4128", CONDITIONS["COMP4128"], 65, 6, {2020: [1], 2021: [1], 2022: [1]}),  # requires wam but is bypassed
            Course("COMP3311", CONDITIONS["COMP3311"], 65, 6, {2020: [1, 2, 3], 2021: [1, 2, 3], 2022: [1, 2, 3]}),
            Course("ARTS1360", CONDITIONS["ARTS1360"], 65, 6, {2020: [2], 2021: [2], 2022: [2]}),
        ],
        "3707",
        ["COMPBH"]
    )

def test_infeasable():
    with raises(Exception):
        # no terms have space
        autoplan(
            [Course("MATH1141", CONDITIONS["MATH1141"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),],
            User({
                "program": "3778",
                "specialisations" : ["COMPA1"],
                "courses": {}
            }),
            (2020, 0),
            (2023, 3),
            [
                12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]
        )
    with raises(Exception):
        # never did prereq
        autoplan(
            [Course("MATH1241", CONDITIONS["MATH1241"], 65, 6, {2020: [1, 3], 2021: [1, 3], 2022: [1, 3]}),],
            User({
                "program": "3778",
                "specialisations" : ["COMPA1"],
                "courses": {}
            }),
            (2020, 0),
            (2023, 3),
            [
                12, 20, 20, 20, 12, 20, 20, 20, 10, 20, 20, 20
            ]
        )

def assert_autoplanning_guarantees(uoc_max: list[int], courses: list[Course], program: str, specialisations: list[str]):
    res = autoplan(
        courses,
        User({
            "program": program,
            "specialisations" : specialisations,
            "courses": {}
        }),
        (2020, 0),
        (2023, 3),
        uoc_max
    )

    assert isinstance(res, list)  # is feasible
    assert len(courses) == len(res)  # all courses listed
    # never breach UOC
    for index, number in enumerate(uoc_max):
        course_names = [course[0] for course in res if terms_between((2020, 0), course[1]) == index]
        assert number >= sum(get_uoc(course_name, courses) for course_name in course_names)
    # all courses valid
    plan: RawUserPlan = [[{}, {}, {}, {}] for _ in range(2023-2020)]
    for course_name, (course_year, course_term) in res:
        plan[course_year - 2020][course_term][course_name] = (get_uoc(course_name, courses), get_mark(course_name, courses))
    assert all(course_state.is_accurate for course_state in validate_terms(
        programCode="3778",
        specs=["COMPA1"],
        plan=plan
    ).values())
