import os

import datetime
from typing import Union

from bson import CodecOptions
from bson.binary import UuidRepresentation

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .constants import COURSES_COL_NAME, PROGRAMS_COL_NAME, REFRESH_TOKENS_COL_NAME, SESSIONS_COL_NAME, SPECS_COL_NAME, USERS_COL_NAME
from .col_types import GuestSessionInfoDict, NotSetupSessionInfoDict, NotSetupUserInfoDict, RefreshTokenInfoDict, SessionInfoDict, UserInfoDict

client: MongoClient

db: Database
archivesDB: Database
usersDB: Database

programsCOL: Collection
specialisationsCOL: Collection
coursesCOL: Collection

sessionsCOL: Collection[Union[NotSetupSessionInfoDict, SessionInfoDict, GuestSessionInfoDict]]
refreshTokensCOL: Collection[RefreshTokenInfoDict]
usersCOL: Collection[Union[NotSetupUserInfoDict, UserInfoDict]]

def connect():
    # TODO-OLLI(pm): this global list is horrible...
    global client, db, archivesDB, usersDB, programsCOL, specialisationsCOL, coursesCOL, sessionsCOL, refreshTokensCOL, usersCOL
    print("Trying to connect to mongo database.")

    # this should raise error if this fails, this is better than exit(1)
    client = MongoClient(f'mongodb://{os.environ["MONGODB_USERNAME"]}:{os.environ["MONGODB_PASSWORD"]}@{os.environ["MONGODB_SERVICE_HOSTNAME"]}:27017')
    print('Connected to mongo database.', client["Main"].command("ping"))

    # setup global variables
    db = client["Main"]
    archivesDB = client["Archives"]
    usersDB = client["Users"]

    programsCOL = db[PROGRAMS_COL_NAME]
    specialisationsCOL = db[SPECS_COL_NAME]
    coursesCOL = db[COURSES_COL_NAME]

    sessionsCOL = usersDB[SESSIONS_COL_NAME].with_options(
        codec_options=CodecOptions(
            tz_aware=True,
            tzinfo=datetime.timezone.utc,
            uuid_representation=UuidRepresentation.STANDARD,
        ),
    )

    refreshTokensCOL = usersDB[REFRESH_TOKENS_COL_NAME].with_options(
        codec_options=CodecOptions(
            tz_aware=True,
            tzinfo=datetime.timezone.utc,
            uuid_representation=UuidRepresentation.STANDARD,
        )
    )

    usersCOL = usersDB[USERS_COL_NAME]


connect()
