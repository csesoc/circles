from time import time
from typing import Optional
from uuid import UUID

from server.db.redis.conn import sdb
from redis.commands.search.query import Query
from .models import SessionID, SessionToken, SessionTokenInfoModel

# TODO-OLLI(pm): remove these comments
# FT.CREATE idx:uid ON HASH PREFIX 1 "stoken:" NOOFFSETS NOHL NOFIELDS NOFREQS STOPWORDS 0 SCHEMA uid TAG CASESENSITIVE
# FT.SEARCH idx:uid "@uid:{z5362383}" NOCONTENT VERBATIM
# FT.SEARCH idx:sid "@sid:{bf362dd3\\-046a\\-49e4\\-8d63\\-fd379f06a40f}" NOCONTENT VERBATIM
# HMGET stoken:Nj-C2n8JYS4imxlVn7WhSX5Pa0uRZ1awa1w_YA-vnN4jMXXqqKVb7HW9rNhfGako sid uid

DELETE_BATCH_SIZE = 100

def form_key(token: SessionToken) -> str:
    return f"token:{token}"

def get_token_info(token: SessionToken) -> Optional[SessionTokenInfoModel]:
    res = sdb.hmget(form_key(token), ["sid", "uid", "exp"])
    assert isinstance(res, list) and len(res) == 3

    sid, uid, exp = res[0], res[1], res[2]
    if sid is None or uid is None or exp is None:
        return None
    if int(exp) <= int(time()):
        return None

    return SessionTokenInfoModel(
        sid=SessionID(UUID(hex=sid)),
        uid=uid,
        exp=int(exp)
    )

def set_token_nx(token: SessionToken, info: SessionTokenInfoModel) -> bool:
    # tries and sets the information, returning whether it was successful
    # if can set first one, assume can set them all
    # TODO-OLLI(pm): figure out how to make this a transaction and/or redis func so it dont get deleted midway
    key = form_key(token)
    exists = sdb.hsetnx(name=key, key="sid", value=info.sid.hex)

    assert isinstance(exists, int)
    if exists == 0:
        return False

    res = sdb.hset(name=key, mapping={
        "uid": info.uid,
        "exp": info.exp,
    })
    assert isinstance(res, int) and res == 2

    exp_res = sdb.expireat(key, info.exp)
    assert isinstance(exp_res, bool) and exp_res

    return True

def delete_all_tokens(sid: SessionID) -> None:
    # FT.SEARCH idx:sid "@sid:{bf362dd3\\-046a\\-49e4\\-8d63\\-fd379f06a40f}" NOCONTENT VERBATIM
    # TODO-OLLI(pm): functionize this
    # look up all the keys, do in patches of DELETE_BATCH_SIZE
    while True:
        all_matches = sdb.ft("idx:sid").search(
            query=Query(f"@sid:{{{sid.hex}}}").no_content().verbatim().paging(0, DELETE_BATCH_SIZE),
        )

        # the type bindings are wrong, the result has the shape
        #  {'attributes': [], 'total_results': 1, 'format': 'STRING', 'results': [{'id': '...', 'values': [...]}], 'warning': []}
        assert isinstance(all_matches, dict)
        if all_matches['total_results'] > 0:
            # delete them all
            # NOTE: potentially this wont work after 1GB worth of keys...
            sdb.delete(*(m["id"] for m in all_matches["results"]))

        if all_matches['total_results'] <= DELETE_BATCH_SIZE:
            return  # no more to delete
