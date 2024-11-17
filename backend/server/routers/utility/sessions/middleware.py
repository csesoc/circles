from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, Request, Response
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from starlette.status import HTTP_401_UNAUTHORIZED

from server.config import SECURE_COOKIES
from server.db.helpers.models import SessionToken

from .errors import ExpiredSessionTokenError
from .interface import get_token_info

def extract_bearer_token(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)
    if not (authorization and scheme and credentials and scheme.lower() == "bearer" and credentials != ""):
        return None
    return credentials

class HTTPBearer401(SecurityBase):
    # remake because of: https://github.com/tiangolo/fastapi/issues/10177
    def __init__(
        self,
        *,
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat="Bearer")
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        # get the token out of the header
        token = extract_bearer_token(request)
        if token is None:
            if self.auto_error:
                # https://www.rfc-editor.org/rfc/rfc9110#name-401-unauthorized
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Token was not given in correct format.",
                    headers={ "WWW-Authenticate": "Bearer" },
                )

            return None

        return token

class HTTPBearerToUserID(HTTPBearer401):
    def __init__(self):
        super().__init__(scheme_name="HTTPBearer401", auto_error=True)

    async def __call__(self, request: Request) -> str:
        token = await super().__call__(request)
        assert token is not None

        try:
            uid, _ = get_token_info(SessionToken(token))
        except ExpiredSessionTokenError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Provided token was expired, please re-authenticate.",
                headers={ "WWW-Authenticate": "Bearer" },
            ) from e

        return uid

def set_secure_cookie(res: Response, key: str, value: Optional[str], expiry: Optional[int] = None) -> None:
    if value is not None and expiry is not None:
        res.set_cookie(
            key=key,
            value=value,
            secure=SECURE_COOKIES,
            httponly=True,
            expires=datetime.fromtimestamp(expiry, tz=timezone.utc),
            samesite="strict",
            # domain="circlesapi.olllli.app",
        )
    else:
        # nothing was given, delete it instead
        # need all the attributes so prefix actually allows it to be set
        res.delete_cookie(
            key=key,
            secure=SECURE_COOKIES,
            httponly=True,
            samesite="strict",
        )
