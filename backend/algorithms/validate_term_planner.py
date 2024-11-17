from typing import Optional
from algorithms.objects.user import User
from server.routers.model import CACHED_HANDBOOK_NOTE, CONDITIONS, CourseState


RawUserPlan = list[list[dict[str, tuple[int, Optional[int]]]]]

def validate_terms(programCode: str, specs: list[str], plan: RawUserPlan) -> dict[str, CourseState]:
    """Validates the term planner, returning all warnings."""
    emptyUserData = {
        "program": programCode,
        "specialisations": specs[:],
        "courses": {},  # Start off the user with an empty year
    }
    user = User(emptyUserData)
    # State of courses on the term planner
    coursesState: dict[str, CourseState] = {}

    for year in plan:
        # Go through all the years
        for term in year:
            user.add_current_courses(term)

            for course in term:
                is_answer_accurate = CONDITIONS.get(course) is not None
                unlocked, warnings = (
                    CONDITIONS[course].validate(user)
                    if is_answer_accurate
                    else (True, [])
                )
                coursesState[course] = CourseState(
                    is_accurate=is_answer_accurate,
                    handbook_note=CACHED_HANDBOOK_NOTE.get(course, ""),
                    unlocked=unlocked,
                    warnings=warnings
                )

            # Add all these courses to the user in preparation for the next term
            user.empty_current_courses()
            user.add_courses(term)
    return coursesState
