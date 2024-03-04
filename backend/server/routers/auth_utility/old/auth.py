""" Routes to deal with user Authentication. """
from datetime import datetime, timezone
from secrets import token_urlsafe
from time import time
from typing import Annotated, Dict, Iterator, List, Literal, Optional, Tuple, TypedDict, cast
from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Request, Response, Security
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from server.routers.user import user_is_setup, default_cs_user, reset, set_user

# from .auth_utility.session_token import SessionError, SessionExpiredOIDC, SessionStorage
from .auth_utility.middleware import HTTPBearer401
from .auth_utility.oidc.requests import UserInfoResponse, exchange_and_validate, generate_oidc_auth_url, get_user_info, validate_authorization_response
from .auth_utility.oidc.errors import OIDCError, OIDCValidationError


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
# sessions = SessionStorage()
require_token = HTTPBearer401()
# validated_uid = SessionTokenValidator(session_store=sessions)
# setup_uid = SessionTokenValidator(session_store=sessions, check_user_is_setup=user_is_setup)


class UnauthorizedModel(BaseModel):
    detail: str

class ForbiddenModel(BaseModel):
    detail: str

class ExchangeCodePayload(BaseModel):
    query_params: Dict[str, str]

class IdentityPayload(BaseModel):
    session_token: str

# @router.delete("/killallsessions")
# def kill_all_sessions():
#     sessions.empty()

@router.get(
    "/identity", 
    response_model=IdentityPayload
)
def get_identity(res: Response, refresh_token: Annotated[Optional[str], Cookie()] = None):
    if refresh_token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is not logged in."
        )

    # generate the new session token
    try:
        ref_tok, ref_exp, ses_tok = sessions.new_session_token(refresh_token)
    except SessionError as e:
        # can either be invalid session token, expired session token, or expired oidc pair
        # TODO: do we want to deal with the other random OIDC errors?
        res.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=e.description,
            headers={ "set-cookie": res.headers["set-cookie"] },
        ) from e

    # set the cookies and return the identity
    res.set_cookie(
        key="refresh_token", 
        value=ref_tok,
        # secure=True,
        httponly=True,
        # domain="circlesapi.csesoc.app",
        expires=datetime.fromtimestamp(ref_exp, tz=timezone.utc),
    )
    return IdentityPayload(session_token=ses_tok)

@router.get(
    "/authorization_url",
    response_model=str
)
def create_auth_url(res: Response) -> str:
    # TODO: check if we want to encrypt this?
    # TODO: make the login page actually use this
    state = token_urlsafe(32)
    auth_url = generate_oidc_auth_url(state)
    expires_at = int(time()) + (10 * 60)

    res.set_cookie(
        key="next_auth_state", 
        value=state,
        # secure=True,
        httponly=True,
        # path="/authorization_url",
        # domain="circlesapi.csesoc.app",
        expires=datetime.fromtimestamp(expires_at, tz=timezone.utc),
    )
    # TODO: sometimes this empty reponses?!
    return auth_url

@router.post(
    "/login", 
    response_model=IdentityPayload
)
def exchange_authorization_code(res: Response, data: ExchangeCodePayload, next_auth_state: Annotated[Optional[str], Cookie()] = None) -> IdentityPayload:
    # TODO: i believe there can be errors before getting here?
    if next_auth_state is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Cookie 'next_auth_state' was missing from request."
        )
    
    try:
        code = validate_authorization_response(next_auth_state, data.query_params)
        token_res = exchange_and_validate(code)
    except OIDCError as e:
        # TODO: finer grain error checks, there are many validation errors possible
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid code. Extra info: {e.error_description}"
        ) from e
    
    token_res, id_token = token_res

    # TODO: do some stuff with the id token here like user database setup

    # set the cookies and respond with the session token
    # TODO: I believe no errors possible here?
    ref_tok, ref_exp, ses_tok = sessions.new_login_session(token_res, id_token)

    # set the cookies and return the identity
    # TODO: delete old state cookie?
    res.set_cookie(
        key="refresh_token", 
        value=ref_tok,
        # secure=True,
        httponly=True,
        # domain="circlesapi.csesoc.app",
        expires=datetime.fromtimestamp(ref_exp, tz=timezone.utc),
    )
    return IdentityPayload(session_token=ses_tok)

@router.delete("/logout")
def logout(res: Response, token: Annotated[str, Security(require_token)]):
    try:
        sessions.destroy_session(token)
        res.delete_cookie("refresh_token")
    except SessionError as e:
        # TODO: do we want to clear cookie here?
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=e.description
        ) from e

@router.get(
    "/userinfo",
    response_model=UserInfoResponse,
)
def user_info(res: Response, user: Annotated[ValidatedToken, Security(validated_uid)]):
    try:
        info = sessions.session_token_to_userinfo(user.token)
        return info
    except SessionExpiredOIDC as e:
        # OIDC has expired and could not be refreshed, hence will be logged out
        res.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=e.description,
            headers={ "set-cookie": res.headers["set-cookie"] },
        ) from e
    except SessionError as e:
        # just the session has expired, will need to call a /identity to continue
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=e.description
        ) from e

@router.get(
    "/validatedUser", 
    response_model=ValidatedToken,
    responses={
        HTTP_401_UNAUTHORIZED: { "model": UnauthorizedModel }
    },
)
def get_validated_user(user: Annotated[ValidatedToken, Security(validated_uid)]):
    return user

@router.get(
    "/checkToken", 
    response_model=None,
    responses={
        HTTP_401_UNAUTHORIZED: { "model": UnauthorizedModel },
        HTTP_403_FORBIDDEN: { "model": ForbiddenModel },
    },
)
def check_token(user: Annotated[ValidatedToken, Security(setup_uid)]):
    # TODO: check it is in database
    return

@router.post('/token')
def create_user_token(token: str):
    print("\n\n\n\n/token called\n\n\n\n")
    set_user(token, default_cs_user())
    reset(token)
