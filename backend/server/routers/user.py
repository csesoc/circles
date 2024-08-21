from itertools import chain
from typing import Annotated, Dict, Optional, cast
from fastapi import APIRouter, HTTPException, Security

from data.processors.models import SpecData
from server.routers.utility import get_all_specialisations, get_course_details
from server.routers.auth_utility.middleware import HTTPBearerToUserID
from server.routers.auth_utility.user import get_setup_user, set_user
from server.routers.model import CourseMark, CourseStorage, DegreeLength, DegreeWizardInfo, HiddenYear, SettingsStorage, StartYear, CourseStorageWithExtra, DegreeLocalStorage, LocalStorage, PlannerLocalStorage, Storage, SpecType

import server.db.helpers.users as udb

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

require_uid = HTTPBearerToUserID()

# Ideally not used often.
@router.post("/saveLocalStorage")
def save_local_storage(localStorage: LocalStorage, uid: Annotated[str, Security(require_uid)]):
    planned: list[str] = sum((sum(year.values(), [])
                             for year in localStorage.planner['years']), [])
    unplanned: list[str] = localStorage.planner['unplanned']
    courses: dict[str, CourseStorage] = {
        course: {
            'code': course,
            'mark': None, # wtf we nuking marks?
            'uoc': get_course_details(course)['UOC'],
            'ignoreFromProgression': False
        }
        for course in chain(planned, unplanned)
    }
    # cancer, but the FE inspired this cancer
    real_planner = localStorage.planner.copy()
    item: Storage = {
        'degree': localStorage.degree,
        'planner': real_planner,
        'courses': courses,
        'settings': SettingsStorage(showMarks=False, hiddenYears=set()),
    }
    set_user(uid, item)


@router.get("/data/all")
def get_user(uid: Annotated[str, Security(require_uid)]) -> Storage:
    return get_setup_user(uid)

@router.get("/data/degree")
def get_user_degree(uid: Annotated[str, Security(require_uid)]) -> DegreeLocalStorage:
    return get_setup_user(uid)['degree']

@router.get("/data/planner")
def get_user_planner(uid: Annotated[str, Security(require_uid)]) -> PlannerLocalStorage:
    return get_setup_user(uid)['planner']

@router.get("/data/courses")
def get_user_p(uid: Annotated[str, Security(require_uid)]) -> Dict[str, CourseStorageWithExtra]:
    # expects to also get the
    # title: str
    # plannedFor: string of form "year term"
    # isMultiterm
    # uoc -> UOC
    # TODO-OLLI(pm): remove the additional data here and get frontend to request it itself
    user = get_setup_user(uid)
    raw_courses = user['courses']
    planner = user['planner']

    # flatten the planner
    flattened: Dict[str, Optional[str]] = { code: None for code in planner['unplanned'] }
    for index, year in enumerate(planner['years']):
        for termIndex, term in year.items():
            for course in term:
                assert course not in flattened  # makes sure its not double storred
                flattened[course] = f"{index + planner['startYear']} {termIndex}"

    res: Dict[str, CourseStorageWithExtra] = {}

    for raw_course in raw_courses.values():
        course_info = get_course_details(raw_course['code'])

        with_extra_info: CourseStorageWithExtra = {
            'code': raw_course['code'],
            'ignoreFromProgression': raw_course['ignoreFromProgression'],
            'mark': raw_course['mark'],
            'uoc': raw_course['uoc'],
            'isMultiterm': course_info['is_multiterm'],
            'title': course_info['title'],
            'plannedFor': flattened.get(raw_course['code']),
        }
        assert raw_course['code'] in flattened, with_extra_info  # ensure it was somewhere

        res[raw_course['code']] = with_extra_info

    return res

@router.get("/data/settings")
def get_user_settings(uid: Annotated[str, Security(require_uid)]) -> SettingsStorage:
    return get_setup_user(uid)['settings']

@router.post("/settings/toggleShowMarks")
def toggle_show_marks(uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['settings'].showMarks = not user['settings'].showMarks
    set_user(uid, user, True)

@router.post("/settings/hideYear")
def hide_year(hidden: HiddenYear, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    if hidden.yearIndex < 0 or hidden.yearIndex >= len(user['planner']['years']):
        raise HTTPException(
            status_code=400, detail=f"Invalid year index '{hidden.yearIndex}'"
        )
    user['settings'].hiddenYears.add(hidden.yearIndex)
    set_user(uid, user, True)

@router.post("/settings/showYears")
def show_years(uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['settings'].hiddenYears = set()
    set_user(uid, user, True)

@router.post("/toggleSummerTerm")
def toggle_summer_term(uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['planner']['isSummerEnabled'] = not user['planner']['isSummerEnabled']
    if not user['planner']['isSummerEnabled']:
        for year in user['planner']['years']:
            user['planner']['unplanned'].extend(year['T0'])
            year['T0'] = []
    set_user(uid, user, True)


@router.put("/updateCourseMark",
            responses={
        400: { "description": "if the mark is invalid or it isn't in the user's courses" },
        200: {
            "description": "on successful update",
        }
    }
)
def update_course_mark(courseMark: CourseMark, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)

    if isinstance(courseMark.mark, int) and (courseMark.mark < 0 or courseMark.mark > 100):
        raise HTTPException(
            status_code=400, detail=f"Invalid mark '{courseMark.mark}'"
        )

    if courseMark.course in user['courses']:
        user['courses'][courseMark.course]['mark'] = courseMark.mark
    else:
        raise HTTPException(
            status_code=400, detail=f"Course code {courseMark.course} was not found in user's courses"
        )

    set_user(uid, user, True)

@router.put("/updateStartYear")
def update_start_year(startYear: StartYear, uid: Annotated[str, Security(require_uid)]):
    """
        Update the start year the user is taking.
        The degree length stays the same and the contents are shifted to fit the new start year.
    """
    user = get_setup_user(uid)
    user['planner']['startYear'] = startYear.startYear
    set_user(uid, user, True)

@router.put("/updateDegreeLength")
def update_degree_length(degreeLength: DegreeLength, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    if len(user['planner']['years']) == degreeLength.numYears:
        return
    diff = degreeLength.numYears - len(user['planner']['years'])
    if diff > 0:
        user['planner']['years'] += ([{"T0": [],
                                     "T1": [], "T2": [], "T3": []}] * diff)
    else:
        for year in user['planner']['years'][diff:]:
            for term in year.values():
                user['planner']['unplanned'].extend(term)
        user['planner']['years'] = user['planner']['years'][:diff]

        user['settings'].hiddenYears = set(
            yearIndex
            for yearIndex in user['settings'].hiddenYears
            if yearIndex < degreeLength.numYears
        )
    set_user(uid, user, True)

@router.put("/setProgram")
def setProgram(programCode: str, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['degree']['programCode'] = programCode
    set_user(uid, user, True)

@router.put("/addSpecialisation")
def addSpecialisation(specialisation: str, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    user['degree']['specs'].append(specialisation)
    set_user(uid, user, True)

@router.put("/removeSpecialisation")
def removeSpecialisation(specialisation: str, uid: Annotated[str, Security(require_uid)]):
    user = get_setup_user(uid)
    specs = user['degree']['specs']
    if specialisation in specs:
        specs.remove(specialisation)
    set_user(uid, user, True)

@router.post("/reset")
def reset(uid: Annotated[str, Security(require_uid)]):
    """Resets user data of a parsed token"""
    assert udb.reset_user(uid)

@router.get("/isSetup")
def is_setup(uid: Annotated[str, Security(require_uid)]) -> bool:
    """Returns whether the user has been setup with a degree yet, replacing old `isComplete` field."""
    return udb.user_is_setup(uid)

@router.post("/setupDegreeWizard", response_model=Storage)
def setup_degree_wizard(wizard: DegreeWizardInfo, uid: Annotated[str, Security(require_uid)]):
    # NOTE: is allowed to be called on a already setup user
    # validate
    num_years = wizard.endYear - wizard.startYear + 1
    if num_years < 1:
        raise HTTPException(status_code=400, detail="Invalid year range")

    # Ensure that all specialisations are valid
    # Need a bidirectoinal validate
    # All specs in wizard (lhs) must be in the RHS
    # All specs in the RHS that are "required" must have an associated LHS selection

    # Keys in the specInfo
    # - 'specs': List[str] - name of the specialisations - thing that matters
    # - 'notes': str - dw abt this (Fe's prob tbh)
    # - 'is_optional': bool - if true then u need to validate associated elem in LHS

    avail_specs = get_all_specialisations(wizard.programCode)
    if avail_specs is None:
        raise HTTPException(status_code=400, detail="Invalid program code")

    flattened_containers = [
        {
            "is_optional": program_sub_container["is_optional"],
            "spec_codes": list(program_sub_container["specs"].keys())
        }
        for spec_type_container in cast(dict[SpecType, dict[str, SpecData]], avail_specs).values()
        for program_sub_container in spec_type_container.values()
    ]

    invalid_lhs_specs = set(wizard.specs).difference(
        spec_code
        for container in flattened_containers
        for spec_code in container["spec_codes"]
    )

    spec_reqs_not_met = [
        container
        for container in flattened_containers
        if (
            not container["is_optional"]
            and not set(container["spec_codes"]).intersection(wizard.specs)
        )
    ]

    # ceebs returning the bad data because FE should be valid anyways
    if invalid_lhs_specs or spec_reqs_not_met:
        raise HTTPException(status_code=400, detail="Invalid specialisations")
    print("Valid specs")

    planner: PlannerLocalStorage = {
        'unplanned': [],
        'isSummerEnabled': False,
        'startYear': wizard.startYear,
        'lockedTerms': {},
        'years': [],
    }

    planner['years'] = [
        {"T0": [], "T1": [], "T2": [], "T3": []}
        for _ in range(num_years)
    ]

    user: Storage = {
        'degree': {
            'programCode': wizard.programCode,
            'specs': wizard.specs,
        },
        'planner': planner,
        'courses': {},
        'settings': SettingsStorage(showMarks=False, hiddenYears=set()),
    }
    set_user(uid, user, True)
    return user
