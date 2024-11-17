import json

from fastapi import APIRouter, HTTPException
from server.db.mongo.conn import coursesCOL

router = APIRouter(
    prefix="/followups",
    tags=["followups"],
)

def get_next_term(term: str) -> str:

    terms = ['S', 'T1', 'T2', 'T3']
    try:
        return terms[(terms.index(term) + 1) % 4]
    except ValueError:
        return "invalid_term"


EnrolmentDataT = dict[str, dict[str, list[str]]]
@router.get(
    "/getFollowups/{origin_course}/{origin_term}",
    responses={
        200: {
            "description": "Returns a list of the most popular followup courses",
            "content": {
                "application/json": {
                    "example": {
                        "originCourse": "COMP1511",
                        "originTerm": "T2",
                        "followups": {
                            "COMP1521": {
                                "T3": 339,
                            },
                            "COMP1531": {
                                "T3": 200,
                            },
                            "COMP2521": {
                                "T3": 120,
                            },
                            "COMP1511": {
                                "T3": 45,
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_followups(origin_course: str, origin_term: str) -> dict[str, str | dict[str, dict[str, int]]]:
    # origin_term is the term that the original course was/would be taken in

    next_term = get_next_term(origin_term)

    if next_term == 'invalid_term':
        raise HTTPException(400, f"Invalid term {origin_term}")

    # we only have enrolment data from T2(2022) -> T3(2022) at this stage
    if origin_term != 'T2':
        raise HTTPException(400, "Data only available from T2")

    # get all comp courses
    all_comp_courses = filter(lambda course: course.startswith("COMP"),
                              [course["code"] for course in coursesCOL.find()])

    if origin_course not in all_comp_courses:
        raise HTTPException(400, f"Invalid COMP course {origin_course}")

    # get enrolment data
    # TODO: Add Enrolment Data back
    with open("./data/final_data/enrolmentData.json", "r", encoding="utf8") as enrolment_data_file:
        enrolment_data: EnrolmentDataT = json.load(enrolment_data_file)

    origin_course_members = enrolment_data.get(origin_course, {}).get(origin_term, [])
    # origin_course_members = enrolment_data[origin_course][origin_term]

    # calculate followups
    followups = {}
    for course in all_comp_courses:
        # count duplicates between:
        #  people who took the origin_course in origin_term
        #  people who took this course in the following term.
        # TODO: this is NOT how next term works!
        # Need to wrap around to next year and whatnot, need better tracking
        # Also, maybe add an inverted index?
        num_followups = len(set(
            get_set_enrolled_in_term(enrolment_data, course, next_term) & set(origin_course_members)
        ))

        if num_followups != 0:
            followups.update({ course: { next_term: num_followups } })

    top_followups = sorted(followups.items(), reverse=True, key=lambda course: course[1][next_term])

    return {
        "originCourse": origin_course,
        "originTerm": origin_term,
        "followups": dict(top_followups),
    }

def get_set_enrolled_in_term(
    enrolment_data: EnrolmentDataT,
    course: str,
    term: str
) -> set[str]:
    return set(enrolment_data.get(course, {}).get(term, []))
