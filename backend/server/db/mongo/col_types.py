from datetime import datetime
from typing import Dict, List, Literal, TypedDict, Union
from uuid import UUID

class RefreshTokenInfoDict(TypedDict):
    token: str
    sid: UUID
    expiresAt: datetime

class SessionInfoOIDCInfoDict(TypedDict):
    accessToken: str
    refreshToken: str
    rawIdToken: str
    validatedIdToken: dict

class SessionInfoDict(TypedDict):
    sid: UUID
    uid: str
    expiresAt: datetime
    currRefreshToken: str
    oidcInfo: SessionInfoOIDCInfoDict
    type: Literal['csesoc']

class NotSetupSessionInfoDict(TypedDict):
    sid: UUID
    uid: str
    expiresAt: datetime
    type: Literal['notsetup']

class GuestSessionInfoDict(TypedDict):
    sid: UUID
    uid: str
    expiresAt: datetime
    currRefreshToken: str
    type: Literal['guest']

class NotSetupUserInfoDict(TypedDict):
    uid: str
    setup: Literal[False]
    guest: bool

class UserDegreeInfoDict(TypedDict):
    programCode: str
    specs: List[str]
    isComplete: bool

class UserCourseInfoDict(TypedDict):
    code: str
    suppressed: bool
    mark: Union[Literal['SY', 'FL', 'PS', 'CR', 'DN', 'HD'], int, None]
    uoc: int
    ignoreFromProgression: bool

class YearTermDict(TypedDict):
    Y: int
    T: int

class PlannerYearDict(TypedDict):
    T0: List[str]
    T1: List[str]
    T2: List[str]
    T3: List[str]

class UserPlannerInfoDict(TypedDict):
    unplanned: List[str]
    startYear: int
    isSummerEnabled: bool
    mostRecentPastTerm: YearTermDict
    years: List[PlannerYearDict]
    lockedTerms: Dict[str, bool]

class UserInfoDict(TypedDict):
    uid: str
    setup: Literal[True]
    guest: bool
    degree: UserDegreeInfoDict
    courses: Dict[str, UserCourseInfoDict]
    planner: UserPlannerInfoDict
