""" Routes to deal with user Authentication. """
from typing import Annotated, Dict, Optional, Tuple, Union, cast
from secrets import token_hex, token_urlsafe
from time import time
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Security
from fastapi_limiter.depends import RateLimiter # type: ignore
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from server.config import SECURE_COOKIES
from server.db.helpers.models import NotSetupUserStorage, GuestSessionInfoModel, RefreshToken, SessionID, SessionInfoModel, SessionOIDCInfoModel, SessionToken
from server.db.helpers.users import delete_user, insert_new_user

from .utility.sessions.errors import ExpiredRefreshTokenError, ExpiredSessionTokenError, OldRefreshTokenError
from .utility.sessions.interface import create_new_guest_token_pair, get_session_info_from_refresh_token, get_session_info_from_session_token, logout_session, setup_new_csesoc_session, create_new_csesoc_token_pair, setup_new_guest_session

from .utility.sessions.middleware import HTTPBearer401, set_secure_cookie
from .utility.oidc.requests import DecodedIDToken, exchange_and_validate, generate_oidc_auth_url, get_userinfo_and_validate, refresh_and_validate, revoke_token, validate_authorization_response
from .utility.oidc.errors import OIDCInvalidGrant, OIDCInvalidToken, OIDCTokenError, OIDCValidationError


REFRESH_TOKEN_COOKIE = f"{"__Host-" if SECURE_COOKIES else ""}refresh-token"
AUTH_STATE_COOKIE = f"{"__Host-" if SECURE_COOKIES else ""}auth-state"
AUTH_STATE_COOKIE_TTL = 10 * 60 # seconds


class UnauthorizedErrorModel(BaseModel):
    detail: str

class ForbiddenErrorModel(BaseModel):
    detail: str

class ExchangeCodePayload(BaseModel):
    oidc_response: Dict[str, str]

class IdentityPayload(BaseModel):
    session_token: str
    exp: int
    uid: str

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

require_token = HTTPBearer401()

# TODO-OLLI(pm): do i want to make a auth helper file
def insert_new_guest_user() -> str:
    # returns the claimed uid
    # TODO-OLLI(pm): i could use uuid, but they long as hell, happy to change this
    data = NotSetupUserStorage(guest=True)

    uid = f"guest{token_hex(4)}"
    while not insert_new_user(uid, data):
        print("guest uid collision", uid)
        uid = f"guest{token_hex(4)}"

    return uid

def _check_csesoc_oidc_session(oidc_info: SessionOIDCInfoModel) -> Optional[SessionOIDCInfoModel]:
    try:
        # TODO: update user's personal details with this info once we have stuff to store
        _ = get_userinfo_and_validate(cast(DecodedIDToken, oidc_info.validated_id_token), oidc_info.access_token)

        return oidc_info  # no need for new info
    except OIDCInvalidToken:
        # access token has expired, try refresh
        # will raise if could not refresh
        try:
            refreshed, validated = refresh_and_validate(cast(DecodedIDToken, oidc_info.validated_id_token), oidc_info.refresh_token)

            return SessionOIDCInfoModel(
                access_token=refreshed["access_token"],
                raw_id_token=refreshed["id_token"],
                refresh_token=refreshed["refresh_token"],
                validated_id_token=cast(dict, validated),
            )
        except OIDCInvalidGrant:
            # refresh token has expired, any other errors are bad and should be handled else ways
            # revoke_token(oidc_info.refresh_token, "refresh_token")  # NOTE: if the fresh token is invalid, i give up
            return None

def _try_get_session_info_for_logout(session_token: SessionToken, refresh_token: Optional[RefreshToken] = None) -> Optional[Tuple[SessionID, Union[SessionInfoModel, GuestSessionInfoModel]]]:
    try:
        # get the user id and the session id from the session token first
        return get_session_info_from_session_token(session_token)
    except ExpiredSessionTokenError:
        pass

    if refresh_token is not None:
        try:
            # Session token failed, we can give up here if we want since cookie will die...
            # but since we might get the refresh_token regardless due to credentials, try use this instead.
            # Thus this is only necessary if we care about removing the rare hanging session...
            return get_session_info_from_refresh_token(refresh_token)
        except (ExpiredRefreshTokenError, OldRefreshTokenError):
            pass

    return None




@router.post('/guest_login', dependencies=[Depends(RateLimiter(times=1, hours=1))])
def create_guest_session(res: Response) -> IdentityPayload:
    # create new login session for user in db, generating new tokens
    uid = insert_new_guest_user()
    new_session_token, session_expiry, new_refresh_token, refresh_expiry = setup_new_guest_session(uid)

    # TODO-OLLI(pm): setting up proper logging

    # set the cookies and return the identity
    set_secure_cookie(res, REFRESH_TOKEN_COOKIE, new_refresh_token, refresh_expiry)
    return IdentityPayload(session_token=new_session_token, exp=session_expiry, uid=uid)



@router.post("/refresh", response_model=IdentityPayload)
def refresh(res: Response, refresh_token: Annotated[Optional[RefreshToken], Cookie(alias=REFRESH_TOKEN_COOKIE)] = None) -> IdentityPayload:
    # refresh flow - returns a new identity given the circles refresh token
    if refresh_token is None or len(refresh_token) == 0:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is not logged in.",
            headers={ "WWW-Authenticate": "Bearer" },
        )

    # generate the token pair
    # first get the oidc session details, this will check if it hasnt expired
    try:
        sid, session_info = get_session_info_from_refresh_token(refresh_token)
    except (ExpiredRefreshTokenError, OldRefreshTokenError) as e:
        # if old refresh token, will destroy the session on the backend
        set_secure_cookie(res, REFRESH_TOKEN_COOKIE, None)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="This refresh token was invalid.",
            headers={ "WWW-Authenticate": "Bearer", "set-cookie": res.headers["set-cookie"] },
        ) from e

    if session_info.type == "csesoc":
        # then check if it is still valid with federated auth
        #   if not, refresh it and update the oidc session details
        new_oidc_info = _check_csesoc_oidc_session(session_info.oidc_info)
        if new_oidc_info is None:
            logout_session(sid)
            set_secure_cookie(res, REFRESH_TOKEN_COOKIE, None)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Session could not be refreshed, please log in again.",
                headers={ "WWW-Authenticate": "Bearer", "set-cookie": res.headers["set-cookie"] },
            )

        # if here, the oidc session was still valid. Create the new token pair
        new_session_token, session_expiry, new_refresh_token, refresh_expiry = create_new_csesoc_token_pair(sid, new_oidc_info)
    else:
        # guest sessions don't have any external authorization linked to them, so easy
        assert isinstance(session_info, GuestSessionInfoModel)
        new_session_token, session_expiry, new_refresh_token, refresh_expiry = create_new_guest_token_pair(sid)

    # set the cookies and return the identity
    set_secure_cookie(res, REFRESH_TOKEN_COOKIE, new_refresh_token, refresh_expiry)
    return IdentityPayload(session_token=new_session_token, exp=session_expiry, uid=session_info.uid)



@router.get("/authorization_url", response_model=str)
def create_auth_url(res: Response) -> str:
    # TODO-OLLI(pm): do i want to make this into a proper redirect?
    state = token_urlsafe(32)
    auth_url = generate_oidc_auth_url(state)
    expires_at = int(time()) + AUTH_STATE_COOKIE_TTL

    set_secure_cookie(res, AUTH_STATE_COOKIE, state, expires_at)
    return auth_url



@router.post("/login", response_model=IdentityPayload)
def login(res: Response, payload: ExchangeCodePayload, next_auth_state: Annotated[Optional[str], Cookie(alias=AUTH_STATE_COOKIE)] = None) -> IdentityPayload:
    if next_auth_state is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Cookie 'next_auth_state' was missing from request."
        )

    try:
        # validate params given in the payload
        auth_code = validate_authorization_response(next_auth_state, payload.oidc_response)
    except OIDCValidationError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Could not validate your params, please try again."
        ) from e

    try:
        # exchange the auth code for tokens and validate them
        tokens, id_token = exchange_and_validate(auth_code)
    except OIDCInvalidGrant as e:
        # the auth code was invalid
        set_secure_cookie(res, AUTH_STATE_COOKIE, None)
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid request, please try again.",
            headers={ "set-cookie": res.headers["set-cookie"] },
        ) from e
    except (OIDCTokenError, OIDCValidationError) as e:
        # might want to refine these error checks, but all are pretty bad
        print(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not exchange tokens, contact admin please.",
        ) from e

    # insert new user into database if it does not exist, will collide if it already does which is good
    uid = id_token["sub"]
    insert_new_user(uid, NotSetupUserStorage(guest=False))

    # create new login session for user in db, generating new tokens
    new_oidc_info = SessionOIDCInfoModel(
        access_token=tokens["access_token"],
        raw_id_token=tokens["id_token"],
        refresh_token=tokens["refresh_token"],
        validated_id_token=cast(dict, id_token),
    )
    new_session_token, session_expiry, new_refresh_token, refresh_expiry = setup_new_csesoc_session(uid, new_oidc_info)

    # set the cookies and return the identity
    set_secure_cookie(res, AUTH_STATE_COOKIE, None)
    set_secure_cookie(res, REFRESH_TOKEN_COOKIE, new_refresh_token, refresh_expiry)
    return IdentityPayload(session_token=new_session_token, exp=session_expiry, uid=uid)



@router.post("/logout", response_model=None)
def logout(res: Response, token: Annotated[SessionToken, Security(require_token)], refresh_token: Annotated[Optional[RefreshToken], Cookie(alias=REFRESH_TOKEN_COOKIE)] = None):
    # delete the cookie first since this should always happen
    set_secure_cookie(res, REFRESH_TOKEN_COOKIE, None)

    session = _try_get_session_info_for_logout(token, refresh_token)
    if session is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Provided token was expired, please re-authenticate.",
            headers={ "WWW-Authenticate": "Bearer", "set-cookie": res.headers["set-cookie"] },
        )

    # kill our session, then revoke the oidc tokens
    # done in this order since once our session is destroyed, their oidc tokens are gone anyway
    sid, session_info = session
    assert logout_session(sid)

    if session_info.type == "guest":
        # a guest user only ever gets one login session, so we can safely drop their data after a successful logout
        assert delete_user(session_info.uid)
    if session_info.type == "csesoc":
        # only need to revoke a token for fed auth sessions
        try:
            revoke_token(session_info.oidc_info.refresh_token, "refresh_token")
        except OIDCInvalidGrant as e:
            # invalid grant could happen if the oidc token is expired, thats fine
            # NOTE: i dont think we want to throw error if it is invalid? but its fine i guess
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Your csesoc session has expired, please re-login.",
                headers={ "WWW-Authenticate": "Bearer", "set-cookie": res.headers["set-cookie"] },
            ) from e
        except OIDCTokenError as e:
            # cant imagine what error this could be, but if it happens, its bad
            print(e)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Please contact server admin, something went wrong",
                headers={ "set-cookie": res.headers["set-cookie"] },
            ) from e
