from fastapi import APIRouter, Response

from server.routers.auth import REFRESH_TOKEN_COOKIE, IdentityPayload, insert_new_guest_user
from server.routers.utility.sessions.interface import setup_new_guest_session
from server.routers.utility.sessions.middleware import set_secure_cookie


router = APIRouter(
    prefix="/dev",
    tags=["dev"],
)

@router.post('/guest_login')
def create_guest_session(res: Response) -> IdentityPayload:
    # create new login session for user in db, generating new tokens
    uid = insert_new_guest_user()
    new_session_token, session_expiry, new_refresh_token, refresh_expiry = setup_new_guest_session(uid)

    # TODO-OLLI(pm): setting up proper logging

    # set the cookies and return the identity
    set_secure_cookie(res, REFRESH_TOKEN_COOKIE, new_refresh_token, refresh_expiry)
    return IdentityPayload(session_token=new_session_token, exp=session_expiry, uid=uid)
