import datetime
from time import time
from typing import Optional

import pymongo
import pymongo.errors

from server.db.mongo.conn import refreshTokensCOL

from .models import RefreshToken, RefreshTokenInfoModel, SessionID

def get_refresh_token_info(token: RefreshToken) -> Optional[RefreshTokenInfoModel]:
    info = refreshTokensCOL.find_one({ 'token': token })

    if info is None:
        return None

    exp = int(info["expiresAt"].timestamp())
    if exp <= int(time()):
        return None

    return RefreshTokenInfoModel(
        sid=SessionID(info["sid"]),
        expires_at=exp,
    )

def insert_refresh_token_info(token: RefreshToken, info: RefreshTokenInfoModel) -> bool:
    try:
        refreshTokensCOL.insert_one({
            "token": token,
            "sid": info.sid,
            "expiresAt": datetime.datetime.fromtimestamp(info.expires_at, tz=datetime.timezone.utc),
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        # token already existed
        return False

def delete_all_refresh_tokens(sid: SessionID) -> int:
    res = refreshTokensCOL.delete_many({ "sid": sid })
    return res.deleted_count
