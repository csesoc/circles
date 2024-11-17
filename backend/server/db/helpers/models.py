from typing import Dict, List, Literal, NewType, Optional, Set, Union
from uuid import UUID
from pydantic import BaseModel, field_serializer

#
# NewTypes
#
SessionID = NewType('SessionID', UUID)
SessionToken = NewType('SessionToken', str)
RefreshToken = NewType('RefreshToken', str)

#
# User Storage Models
#
class UserDegreeStorage(BaseModel):
    programCode: str
    specs: List[str]

class UserCourseMinimal(BaseModel):
    mark: Union[Literal['SY', 'FL', 'PS', 'CR', 'DN', 'HD'], int, None]
    ignoreFromProgression: bool

class UserCourseStorage(BaseModel):
    code: str
    mark: Union[Literal['SY', 'FL', 'PS', 'CR', 'DN', 'HD'], int, None]
    uoc: int
    ignoreFromProgression: bool

# TODO-OLLI(pm): https://docs.pydantic.dev/latest/concepts/models/#rootmodel-and-custom-root-types
# we can make this a RootModel or use a TypeAdapter if we want stronger type checks here
type UserCoursesStorage = Dict[str, UserCourseStorage]  # type: ignore

class PlannerYear(BaseModel):
    T0: List[str]
    T1: List[str]
    T2: List[str]
    T3: List[str]

class UserPlannerStorage(BaseModel):
    unplanned: List[str]
    startYear: int
    isSummerEnabled: bool
    years: List[PlannerYear]
    lockedTerms: Dict[str, bool]

class UserSettingsStorage(BaseModel):
    showMarks: bool
    hiddenYears: Set[int]

    @field_serializer('hiddenYears', when_used='always')
    def serialize_hidden_years(self, hiddenYears: Set[int]):
        return sorted(hiddenYears)

class _BaseUserStorage(BaseModel):
    # NOTE: could also put uid here if we want
    guest: bool

class UserImport(BaseModel):
    degree: UserDegreeStorage
    courses: dict[str, UserCourseMinimal]
    planner: UserPlannerStorage
    settings: UserSettingsStorage

class UserStorage(_BaseUserStorage):
    setup: Literal[True] = True
    degree: UserDegreeStorage
    courses: UserCoursesStorage
    planner: UserPlannerStorage
    settings: UserSettingsStorage

class NotSetupUserStorage(_BaseUserStorage):
    setup: Literal[False] = False

# https://github.com/pydantic/pydantic/issues/1223#issuecomment-1152323275
class PartialUserStorage(BaseModel):
    # for batch user storage update
    # TODO-OLLI(pm): remove this and use keyword args since they cannot be None
    degree: Optional[UserDegreeStorage] = None
    courses: Optional[UserCoursesStorage] = None
    planner: Optional[UserPlannerStorage] = None
    settings: Optional[UserSettingsStorage] = None

#
# Session Token Models (redis)
#
class SessionTokenInfoModel(BaseModel):
    sid: SessionID              # id of the session behind this token
    uid: str                    # user who owns the session
    exp: int                    # time of expiry, will be replaced with a TTL on the cache

#
# Refresh Token Models (mongo)
#
class RefreshTokenInfoModel(BaseModel):
    # object stored against the refresh token
    sid: SessionID              # id of the session behind this token
    expires_at: int             # time of expiry, will be replaced with a TTL on the cache

#
# Session Models (mongo)
#
# TODO-OLLI(pm): figure out if we want to actually annotate id token type so no casts needed
class SessionOIDCInfoModel(BaseModel):
    access_token: str           # most recent access token
    raw_id_token: str           # most recent id token string
    refresh_token: str          # most recent refresh token
    validated_id_token: dict    # most recent valid id token object

# TODO-OLLI(pm): use literal around enum values for the discriminators
# (currently pydantic doesn't properly support the enum value serialization)
class NotSetupSessionModel(BaseModel):
    # object stored against the sid when session is not yet setup (brief time between during token generation)
    uid: str                                # for validation and back lookup
    type: Literal['notsetup'] = 'notsetup'  # ensure that this can get parsed correctly
    expires_at: int                         # time of expiry, will be replaced with a TTL on the cache

class SessionInfoModel(BaseModel):
    # object stored against the sid
    uid: str                            # for validation and back lookup
    oidc_info: SessionOIDCInfoModel
    curr_ref_token: RefreshToken        # the most recent refresh token, only one that should be accepted
    type: Literal['csesoc'] = 'csesoc'  # ensure that this can get parsed correctly
    expires_at: int                     # time of expiry, will be replaced with a TTL on the cache

class GuestSessionInfoModel(BaseModel):
    # object stored against the sid
    uid: str                          # for validation and back lookup
    curr_ref_token: RefreshToken      # the most recent refresh token, only one that should be accepted
    type: Literal['guest'] = 'guest'  # ensure that this can get parsed correctly
    expires_at: int                   # time of expiry, will be replaced with a TTL on the cache
