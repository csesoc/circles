# pylint: disable=wrong-import-position
import os

import requests
from dotenv import load_dotenv

load_dotenv("../env/backend.env")  # must be before the connection imports as they require the env
os.environ["SESSIONSDB_SERVICE_HOSTNAME"] = "localhost"
os.environ["MONGODB_SERVICE_HOSTNAME"] = "localhost"

from server.db.mongo.setup import setup_user_related_collections
from server.db.redis.setup import setup_redis_sessionsdb




def clear():
    """drop users in database. Used before every test is run."""
    setup_user_related_collections(drop=True)
    setup_redis_sessionsdb()

def get_token():
    return requests.post('http://127.0.0.1:8000/dev/guest_login', timeout=5000).json()["session_token"]

def get_token_headers(token: str):
    return {"Authorization": f"Bearer {token}"}
