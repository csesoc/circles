"""
Implementation for the 2023 CTF.


Scenario:
    In the whimsical world of the CTF (Capture The Flag), an extraordinary
    challenge awaits our protagonist, Ollie the Otter. Ollie, a brilliant otter
    with a passion for education, has embarked on an academic journey like no
    other. But there's a twist – Ollie's unique otter nature has led to some
    special conditions on his degree planning adventure.

    Ollie's task is to navigate through a degree planner system called
    "Circles," specially designed to accommodate his otter-specific
    requirements. In this intriguing scenario, you must help Ollie, the otter
    scholar, chart his academic path using Circles.

    Ollie is planning his 3 year Computer Science (3778) degree starting in 2024
    and wants to take a Computer Science major and Mathematics minor. Help him set
    up his degree in the degree wizard!

    When you are done, press the `Validate CTF` button on the term planner page
    to recieve your flags.

# Stage 1. The Otter's Academic Odyssey: Charting Uncharted Waters
    Being the pioneer Otter in academia, Ollie faces some unique conditions
    that must be fulfilled for him to successfully navigate his degree. Let's
    tackle parts 0-3 to obtain the first flag.

# Stage 2. The Kafka Quandary: Or How I Learned To Stop Worrying and Love The
# Handbook
    Ollie encounters additional hurdles due to university policies, with
    challenges 4 through 7 directly related to these policy-driven obstacles.
    Join Ollie in overcoming these challenges and guiding him through this
    academic maze

# Stage 3: (HARD) Numbers, Notions, and the Cult of Calculus: An O-Week Odyssey
    During Orientation Week (O-week), Ollie had a chance encounter with a group
    of math students. Little did he know that this encounter would lead to him
    being initiated into a number-centric cult. Over time, Ollie developed
    superstitions about certain numbers, and the ultimate challenges he faces
    revolve around aligning his degree plan with his newfound beliefs. With the
    last challenges, Ollie on his quest to complete his degree while also
    seeking the approval of the enigmatic number cult
"""
from typing import Annotated, Callable, Optional

from fastapi import APIRouter, Security
from server.routers.utility.sessions.middleware import HTTPBearerToUserID
from server.routers.utility.user import get_setup_user
from server.routers.model import Storage

router = APIRouter(
    prefix="/ctf", tags=["ctf"], responses={404: {"description": "Not found"}}
)

require_uid = HTTPBearerToUserID()


def all_courses(data: Storage) -> set[str]:
    """
    Returns all courses from a planner
    """
    return {
        course
        for year in data["planner"]["years"]
        for term in year.values()
        for course in term
    }


def get_code(course: str) -> int:
    """
    Returns the code of a courseCode
    EG: COMP1511 -> 1511
    """
    return int(course[4:])


def get_faculty(course: str) -> str:
    """
    Returns the faculty of a courseCode
    EG: COMP1511 -> COMP
    """
    return course[:4]


def gen_eds(courses: set[str]) -> set[str]:
    """
    Returns all gen eds from a set of courses
    """
    return set(
        course
        for course in courses
        if not course.startswith("COMP") and not course.startswith("MATH")
    )


def hard_requirements(data: Storage) -> bool:
    # NOTE: Can't check start year from this
    # Frontend should handle most of this anyways
    # including validity of the program
    return (
        data["degree"]["programCode"] == "3778"
        and "COMPA1" in data["degree"]["specs"]
        and "MATHC2" in data["degree"]["specs"]
        and len(data["planner"]["years"]) == 3
    )


def extended_courses(data: Storage) -> bool:
    """
    Must take atleast 3 courses with extended in the name
    """
    extended_course_codes = {
        "COMP3821",
        "COMP3891",
        "COMP6841",
        "COMP6843"
        "COMP6845"
    }
    return len(extended_course_codes & all_courses(data)) >= 3


def summer_course(data: Storage) -> bool:
    """
    Must take atleast one summer course
    """
    return any(
        course.startswith("COMP")
        for year in data["planner"]["years"]
        for course in year["T0"]
    )



def term_sums_even(data: Storage) -> bool:
    """
    Check that the sum of the course codes in even terms is even
    """
    is_even: Callable[[int], bool] = lambda x: x % 2 == 0
    return all(
        is_even(sum(map(get_code, term)))
        for year in data["planner"]["years"]
        for term in list(year.values())[2::2]
    )

def term_sums_odd(data: Storage) -> bool:
    """
    Check that the sum of the course codes in odd terms is odd
    """
    is_odd: Callable[[int], bool] = lambda x: x % 2 == 1
    return all(
        is_odd(sum(map(get_code, term)))
        for year in data["planner"]["years"]
        for term in list(year.values())[1::2]
    )

def comp1511_marks(data: Storage) -> bool:
    """
    Ollie must achieve a mark of 100 in COMP1511 to keep his scholarship
    """
    return "COMP1511" in data["courses"] and data["courses"]["COMP1511"]["mark"] == 100


def gen_ed_sum(data: Storage) -> bool:
    """
    The sum of GENED course codes must not exceed 2200
    """
    return sum(map(get_code, gen_eds(all_courses(data)))) <= 2200


def gen_ed_faculty(data: Storage) -> bool:
    """
    Gen-Eds must all be from different faculties
    """
    gen_eds_facs = list(map(get_faculty, gen_eds(all_courses(data))))
    return len(gen_eds_facs) == len(set(gen_eds_facs))


def same_code_diff_faculty(data: Storage) -> bool:
    """
    Must take two courses with the same code but, from different faculties
    """
    codes = list(map(get_code, all_courses(data)))
    # Can't have duplicate of a course since it's a set
    return len(codes) != len(set(codes))


def math_limit(data: Storage) -> bool:
    """
    In your N-th year, you can only take N + 1 math courses
    """
    for i, year in enumerate(data["planner"]["years"], 1):
        # Use sum(1, ...) instead of len to avoid dual allocation
        num_math = sum(
            1
            for term in year.values()
            for course in term
            if course.startswith("MATH")
        )
        if num_math > i + 1:
            return False

    return True

def six_threes_limit(data: Storage) -> bool:
    """
    There can by at most 6 occurrences of the number 3 in the entire
    planner
    """
    all_codes = "".join(str(get_code(course)) for course in all_courses(data))
    return all_codes.count("3") <= 6

def comp1531_third_year(data: Storage) -> bool:
    """
    COMP1531 must be taken in the third year
    """
    if len(data["planner"]["years"]) < 3:
        return False

    third_year = data["planner"]["years"][2]
    return any(
        "COMP1531" in term
        for term in third_year.values()
    )

ValidatorFn = Callable[[Storage], bool]
ObjectiveMessage = str
Flag = str
requirements: list[tuple[ValidatorFn, ObjectiveMessage, Optional[Flag]]] = [
    # Challenge 1
    (hard_requirements, "Before you can submit, you must check that you are in a 3 year CS degree and have a math minor", None),
    (summer_course, "Ollie must take one summer COMP course.", None),
    (comp1511_marks, "To keep their scholarship, Ollie must achieve a mark of 100 in COMP1511.", None),
    (extended_courses, "Ollie must complete at least THREE COMP courses with extended in the name that have not been discontinued.", "levelup{mVd3_1t_2_un1}"),
    # Challenge 2
    (comp1531_third_year, "Unable to find a partner earlier, Ollie must take COMP1531 in their third year.", None),
    (gen_ed_faculty, "The university has decided that General Education must be very general. As such, each Gen-Ed unit that Ollie takes must be from a different faculty.", None),
    (math_limit, "The university has become a big believer in spaced repetition and want to prevent students from cramming subjects for their minors. Now, in their N-th year, Ollie can only take N + 1 math courses.", None),
    (gen_ed_sum, "Course codes now reflect the difficulty of a course. To avoid extremely stressful terms, the sum of Olli's Gen-Ed course codes must not exceed 2200.", "levelup{i<3TryMesters}"),
    # Challenge 3
    (same_code_diff_faculty, "You must take two courses from different faculties that have the same course code.", None),
    (term_sums_even, "You must ensure that the sum of your course codes in even terms is even. Note that summer courses do not count towards this.", None),
    (term_sums_odd, "You must ensure that the sum of your course codes in odd terms is odd. Note that summer courses do not count towards this.", None),
    (six_threes_limit, "In all your course codes, there can be at most 6 occurrences of the number 3", "levelup{CU1Tur3d}"),
]

@router.post("/validateCtf/")
def validate_ctf(uid: Annotated[str, Security(require_uid)]):
    """
    Validates the CTF
    """

    data = get_setup_user(uid)
    passed: list[str] = []
    flags: list[str] = []
    for req_num, (fn, msg, flag) in enumerate(requirements):
        if not fn(data):
            return {
                "valid": False,
                "passed": passed,
                "failed": req_num,
                "flags": flags,
                "message": msg
            }

        passed.append(msg)
        if flag is not None:
            flags.append(flag)

    return {
        "valid": True,
        "failed": -1,
        "passed": passed,
        "flags": flags,
        "message": "Congratulations! You have passed all the requirements for the CTF."
    }
