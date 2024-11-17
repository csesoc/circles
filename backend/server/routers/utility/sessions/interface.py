from secrets import token_urlsafe
from time import time
from typing import Tuple, Union
from uuid import uuid4

from pydantic import PositiveInt

from server.db.helpers.models import GuestSessionInfoModel, NotSetupSessionModel, RefreshToken, RefreshTokenInfoModel, SessionID, SessionInfoModel, SessionOIDCInfoModel, SessionToken, SessionTokenInfoModel
from server.db.helpers import sessions, refresh_tokens, session_tokens

from .errors import ExpiredRefreshTokenError, ExpiredSessionTokenError, OldRefreshTokenError

DAY = 60 * 60 * 24
SESSION_TOKEN_LIFETIME = 60 * 15   # 15 minutes
REFRESH_TOKEN_LIFETIME = DAY * 30  # 30 days

# db interface function
# WARNING: these do not do any validation (other than ensuring the properties expected)
def _new_token() -> str:
    return token_urlsafe(48)

def _insert_new_session_token_info(sid: SessionID, uid: str, ttl_seconds: PositiveInt) -> Tuple[SessionToken, int]:
    # creates a new session, returning (token, expires_at)
    assert ttl_seconds > 0

    expires_at = int(time()) + ttl_seconds
    info = SessionTokenInfoModel(
        sid=sid,
        uid=uid,
        exp=expires_at,
    )

    token = SessionToken(_new_token())
    while not session_tokens.set_token_nx(token, info):
        print("session token collision", token)
        token = SessionToken(_new_token())

    return (token, expires_at)

def _insert_new_refresh_info(sid: SessionID, ttl_seconds: PositiveInt) -> Tuple[RefreshToken, int]:
    # creates a new session, returning (token, expires_at)
    assert ttl_seconds > 0

    expires_at = int(time()) + ttl_seconds
    info = RefreshTokenInfoModel(
        sid=sid,
        expires_at=expires_at,
    )

    token = RefreshToken(_new_token())
    while not refresh_tokens.insert_refresh_token_info(token, info):
        print("refresh token collision:", token)
        token = RefreshToken(_new_token())

    return (token, expires_at)

def _setup_new_session(uid: str, ttl_seconds: PositiveInt) -> SessionID:
    # allocates a new session, generating the id
    # does not setup the info, as this should be run before we have the curr token
    # the ttl should be specifically how long this fake session lasts, not the future real session
    assert ttl_seconds > 0

    expires_at = int(time()) + ttl_seconds
    info = NotSetupSessionModel(
        uid=uid,
        type="notsetup",
        expires_at=expires_at,
    )

    sid = SessionID(uuid4())
    while not sessions.insert_not_setup_session(sid, info):
        print("session id collision:", sid)
        sid = SessionID(uuid4())

    return sid

def _destroy_session(sid: SessionID) -> bool:
    # destroys all refresh tokens, session tokens, and the session
    # redis will be secondary indexed on the sid, so this wont be too horrible
    session_tokens.delete_all_tokens(sid)
    refresh_tokens.delete_all_refresh_tokens(sid)
    return sessions.delete_all_sessions(sid)


def get_token_info(session_token: SessionToken) -> Tuple[str, SessionID]:
    info = session_tokens.get_token_info(session_token)
    if info is None:
        raise ExpiredSessionTokenError(session_token)

    return (info.uid, info.sid)

def get_session_info_from_refresh_token(refresh_token: RefreshToken) -> Tuple[SessionID, Union[SessionInfoModel, GuestSessionInfoModel]]:
    # useful to check oidc status before refreshing the session
    ref_info = refresh_tokens.get_refresh_token_info(refresh_token)
    if ref_info is None:
        raise ExpiredRefreshTokenError(refresh_token)

    # TODO-OLLI(pm): maybe create an aggregate query for these two steps
    sid = ref_info.sid
    session_info = sessions.get_session_info(sid)
    assert session_info is not None

    if session_info.curr_ref_token != refresh_token:
        # replay attack, destroy entire session
        assert _destroy_session(sid)
        raise OldRefreshTokenError(refresh_token)

    return (sid, session_info)

def get_session_info_from_session_token(session_token: SessionToken) -> Tuple[SessionID, Union[SessionInfoModel, GuestSessionInfoModel]]:
    # NOTE: only should be used for logout, NOT for refreshing
    info = session_tokens.get_token_info(session_token)
    if info is None:
        raise ExpiredSessionTokenError(session_token)

    session_info = sessions.get_session_info(info.sid)
    assert session_info is not None  # NOTE: assertion error here if removed from mongo but not redis...

    return (info.sid, session_info)

def setup_new_csesoc_session(uid: str, oidc_info: SessionOIDCInfoModel) -> Tuple[SessionToken, int, RefreshToken, int]:
    # creates a new login session for this user and oidc pair, returning the tokens and expiry
    # this oidc info should only be used for ONE circles session,
    # and is used to keep track of whether the oidc session is still intact
    # assumes the OIDC info is valid, otherwise the session will just collapse next refresh

    # if we get a faulty oidc token triple, then the session will just collapse next time we try
    sid = _setup_new_session(uid, 120)  # only make it last very briefly
    refresh_token, refresh_expiry = _insert_new_refresh_info(sid, REFRESH_TOKEN_LIFETIME)
    session_token, session_token_expiry = _insert_new_session_token_info(sid, uid, SESSION_TOKEN_LIFETIME)

    # bind the tokens to the session and return, with a session ttl of abit over refresh token for autocleanup
    assert sessions.update_csesoc_session(sid, refresh_expiry + DAY, refresh_token, oidc_info)
    return (session_token, session_token_expiry, refresh_token, refresh_expiry)

def setup_new_guest_session(uid: str) -> Tuple[SessionToken, int, RefreshToken, int]:
    # creates a new login session for this guest user
    # to keep this as seemless as normal csesoc sessions, it will be handled mostly the same except no OIDC steps.
    # In reality, there should never be multiple guest sessions for the same guest uid, but that is ok.

    sid = _setup_new_session(uid, 120)  # only make it last very briefly
    refresh_token, refresh_expiry = _insert_new_refresh_info(sid, REFRESH_TOKEN_LIFETIME)
    session_token, session_token_expiry = _insert_new_session_token_info(sid, uid, SESSION_TOKEN_LIFETIME)

    # bind the tokens to the session and return, with a session ttl of abit over refresh token for autocleanup
    assert sessions.update_guest_session(sid, refresh_expiry + DAY, refresh_token)
    return (session_token, session_token_expiry, refresh_token, refresh_expiry)

def create_new_csesoc_token_pair(sid: SessionID, new_oidc_info: SessionOIDCInfoModel) -> Tuple[SessionToken, int, RefreshToken, int]:
    # generates a new token pair given an existing session
    # again, assumes oidc info is valid, otherwise it will collapse
    # TODO-OLLI(pm): do we want to convert this to a single find_one_and_update?
    session_info = sessions.get_session_info(sid)
    assert session_info is not None  # TODO-OLLI(pm): might happen if they log out before this and after an sid is gotten
    uid = session_info.uid

    # all is good, generate new pair, bind tokens and return
    refresh_token, refresh_expiry = _insert_new_refresh_info(sid, REFRESH_TOKEN_LIFETIME)
    session_token, session_token_expiry = _insert_new_session_token_info(sid, uid, SESSION_TOKEN_LIFETIME)
    assert sessions.update_csesoc_session(sid, refresh_expiry + DAY, refresh_token, new_oidc_info)
    return (session_token, session_token_expiry, refresh_token, refresh_expiry)

def create_new_guest_token_pair(sid: SessionID) -> Tuple[SessionToken, int, RefreshToken, int]:
    # generates a new token pair given an existing session
    # TODO-OLLI(pm): do we want to convert this to a single find_one_and_update?
    session_info = sessions.get_session_info(sid)
    assert session_info is not None  # TODO-OLLI(pm): might happen if they log out before this and after an sid is gotten
    uid = session_info.uid

    # all is good, generate new pair, bind tokens and return
    refresh_token, refresh_expiry = _insert_new_refresh_info(sid, REFRESH_TOKEN_LIFETIME)
    session_token, session_token_expiry = _insert_new_session_token_info(sid, uid, SESSION_TOKEN_LIFETIME)
    assert sessions.update_guest_session(sid, refresh_expiry + DAY, refresh_token)
    return (session_token, session_token_expiry, refresh_token, refresh_expiry)

def logout_session(sid: SessionID) -> bool:
    return _destroy_session(sid)
