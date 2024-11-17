from typing import Optional, Union

import pymongo
import pymongo.errors

from server.db.mongo.constants import UID_INDEX_NAME
from server.db.mongo.conn import usersCOL

from .models import NotSetupUserStorage, PartialUserStorage, UserCoursesStorage, UserDegreeStorage, UserPlannerStorage, UserSettingsStorage, UserStorage

# TODO-OLLI(pm): decide if we want to remove type ignores by constructing dictionaries manually

def get_user(uid: str) -> Optional[Union[NotSetupUserStorage, UserStorage]]:
    res = usersCOL.find_one({ 'uid': uid })
    if res is None:
        return None

    return UserStorage.model_validate(res) if res["setup"] else NotSetupUserStorage.model_validate(res)

def user_is_setup(uid: str) -> bool:
    res = usersCOL.find_one({ 'uid': uid, 'setup': { "$eq": True } })
    return res is not None

def insert_new_user(uid: str, data: NotSetupUserStorage) -> bool:
    try:
        usersCOL.insert_one({
            "uid": uid,
            "guest": data.guest,
            "setup": False,
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        # uid already existed
        return False

def reset_user(uid: str) -> bool:
    res = usersCOL.update_one(
        { "uid": uid },
        {
            "$unset": {
                "degree": "",
                "courses": "",
                "planner": "",
                "settings": "",
            },
            "$set": {
                "setup": False,
            },
        },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def set_user(uid: str, data: UserStorage, overwrite: bool = False) -> bool:
    if overwrite:
        # update/upsert
        res = usersCOL.update_one(
            { "uid": uid },
            {
                "$set": data.model_dump(include={ "degree", "courses", "planner", "settings", "setup" }),
                "$setOnInsert": {
                    # The fields that are usually immutable
                    "uid": uid,
                    "guest": data.guest,
                },
            },
            upsert=True,
            hint=UID_INDEX_NAME,
        )

        return res.matched_count == 1

    # just try insert
    try:
        usersCOL.insert_one(data.model_dump()) # type: ignore
        return True
    except pymongo.errors.DuplicateKeyError:
        # uid already existed
        return False

def update_user_degree(uid: str, data: UserDegreeStorage) -> bool:
    res = usersCOL.update_one(
        { "uid": uid, "setup": True },
        {
            "$set": {
                "degree": data.model_dump(),
            },
        },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def update_user_courses(uid: str, data: UserCoursesStorage) -> bool:
    res = usersCOL.update_one(
        { "uid": uid, "setup": True },
        {
            "$set": {
                "courses": { code: info.model_dump() for code, info in data.items() },
            },
        },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def update_user_planner(uid: str, data: UserPlannerStorage) -> bool:
    res = usersCOL.update_one(
        { "uid": uid, "setup": True },
        {
            "$set": {
                "planner": data.model_dump(),
            },
        },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def update_user_settings(uid: str, data: UserSettingsStorage) -> bool:
    res = usersCOL.update_one(
        { "uid": uid, "setup": True },
        {
            "$set": {
                "settings": data.model_dump(),
            },
        },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def update_user(uid: str, data: PartialUserStorage) -> bool:
    # updates certain properties of the user
    # if enough are given, declares it as setup
    fields = { "courses", "degree", "planner", "settings" }
    payload = {
        k: v
        for k, v
        in data.model_dump(
            include=fields,
            exclude_unset=True,
        ).items()
        if v is not None  # cannot exclude_none since subclasses use None
    }

    if len(payload) == 0:
        # most semantically correct
        return user_is_setup(uid)

    if fields.issubset(payload.keys()):
        # enough to declare user as setup
        payload["setup"] = True

    # if we have enough props to ensure setup, then we only need to find by uid,
    #   otherwise we need to make sure user is already setup
    res = usersCOL.update_one(
        { "uid": uid, "setup": True } if "setup" not in payload else { "uid": uid },
        { "$set": payload },
        upsert=False,
        hint=UID_INDEX_NAME,
    )

    return res.matched_count == 1

def delete_user(uid: str) -> bool:
    res = usersCOL.delete_one(
        { "uid": uid },
        hint=UID_INDEX_NAME,
    )

    return res.deleted_count == 1
