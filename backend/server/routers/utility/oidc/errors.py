from __future__ import annotations
from typing import Any, Dict, Optional

class OIDCError(Exception):
    # base class
    def __init__(self, error_description: Optional[str] = None) -> None:
        self.error_description: Optional[str] = error_description

    def __str__(self) -> str:
        desc = self.error_description or "No description."
        return f"{super().__str__()}\n\tDescription: {desc}"

#
# errors coming from requests
#
class OIDCRequestError(OIDCError):
    def __init__(self, error: str, error_description: Optional[str] = None) -> None:
        super().__init__(error_description)
        self.error_code: str = error

class OIDCUnknownError(OIDCRequestError):
    def __init__(self, error: str = "unknown", error_description: Optional[str] = None, status_code: Optional[int] = None, extra_info: Optional[Any] = None) -> None:
        super().__init__(error, error_description)
        self.status_code = status_code
        self.extra_info = extra_info

# common to all
class OIDCInvalidRequest(OIDCRequestError):
    # never
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("invalid_request", error_description)

# from token exchange, refresh or revoking
# https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
class OIDCTokenError(OIDCRequestError):
    @staticmethod
    def from_dict(error: Dict[str, Any]) -> OIDCRequestError | OIDCUnknownError:
        # pylint: disable=too-many-return-statements  # this is good
        # matches all possible token related error responses
        code = error.get("error")
        description = error.get("error_description")
        match code:
            case "invalid_request":
                return OIDCInvalidRequest(description)
            case "invalid_client":
                return OIDCInvalidClient(description)
            case "invalid_grant":
                return OIDCInvalidGrant(description)
            case "unauthorized_client":
                return OIDCUnauthorizedClient(description)
            case "unsupported_grant_type":
                return OIDCUnsupportedGrantType(description)
            case "invalid_scope":
                return OIDCInvalidScope(description)
            case "unsupported_token_type":
                return OIDCUnsupportedGrantType(description)
            case str():
                return OIDCUnknownError(error=code, error_description=description, extra_info=error)
        return OIDCUnknownError(extra_info=error)

class OIDCInvalidClient(OIDCTokenError):
    # never (ideally)
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("invalid_client", error_description)

class OIDCInvalidGrant(OIDCTokenError):
    # yes, expired credentials
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("invalid_grant", error_description)

class OIDCUnauthorizedClient(OIDCTokenError):
    # never
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("unauthorized_client", error_description)

class OIDCUnsupportedGrantType(OIDCTokenError):
    # never
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("unsupported_grant_type", error_description)

class OIDCInvalidScope(OIDCTokenError):
    # never
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("invalid_scope", error_description)

# https://datatracker.ietf.org/doc/html/rfc7009#section-2.2.1
class OIDCRevokeUnsupportedTokenType(OIDCTokenError):
    # never, also only relevant to revocation
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("unsupported_token_type", error_description)


# from userinfo request
# https://datatracker.ietf.org/doc/html/rfc6750#section-3.1
class OIDCUserInfoError(OIDCRequestError):
    @staticmethod
    def from_dict(error: Dict[str, Any]) -> OIDCRequestError | OIDCUnknownError:
        # matches all possible user info error responses
        code = error.get("error")
        description = error.get("error_description")
        match code:
            case "invalid_request":
                return OIDCInvalidRequest(description)
            case "invalid_token":
                return OIDCInvalidToken(description)
            case "insufficient_scope":
                return OIDCInsufficientScope(description)
            case str():
                return OIDCUnknownError(error=code, error_description=description, extra_info=error)
        return OIDCUnknownError(extra_info=error)

class OIDCInvalidToken(OIDCUserInfoError):
    # yes, when token is invalid
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("invalid_token", error_description)

class OIDCInsufficientScope(OIDCUserInfoError):
    # never (ideally)
    def __init__(self, error_description: Optional[str] = None) -> None:
        super().__init__("insufficient_scope", error_description)

#
# errors from validating the responses
#
class OIDCValidationError(OIDCError):
    def __init__(self, error_description: Optional[str] = None, extra_info: Optional[str] = None) -> None:
        super().__init__(error_description)
        self.extra_info = extra_info
