import os

CLIENT_ID = os.getenv("AUTH_CSE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH_CSE_CLIENT_SECRET")

if CLIENT_ID is None or CLIENT_SECRET is None:
    # TODO: do some proper logging with this
    print("Environment variables 'AUTH_CSE_CLIENT_ID' and 'AUTH_CSE_CLIENT_SECRET' are missing, fedauth will NOT work!!!")

OPENID_CONFIG_URL = "https://id.csesoc.unsw.edu.au/.well-known/openid-configuration"
_REDIRECT_BASE_URI = os.getenv("AUTH_REDIRECT_BASE_URI", "http://localhost:3000")
REDIRECT_URI = f"{_REDIRECT_BASE_URI}/login/success/csesoc"
