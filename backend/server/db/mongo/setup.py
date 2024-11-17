"""Contains all the database and collection instances which can be exported to
other files. Also contains helper functions to read and write from db upon
initialisation.

NOTE: The helper functions must be run from the backend directory due to their paths
"""

import json

from server.config import ARCHIVED_DATA_PATH, FINAL_DATA_PATH
from data.config import ARCHIVED_YEARS

from .constants import COURSES_COL_NAME, PROGRAMS_COL_NAME, REFRESH_TOKENS_COL_NAME, SESSIONS_COL_NAME, SID_INDEX_NAME, SPECS_COL_NAME, TOKEN_INDEX_NAME, UID_INDEX_NAME, USERS_COL_NAME
from .conn import db, archivesDB, usersDB



def _create_users_collection():
    # users {
    #     uid! string,     // unique indexed, the uid we get back from the oidc
    #     info! object,    // extra info that we gather from oidc
    #     degree! { ... },
    #     courses! { ... },
    #     planner! { ... },
    # }
    usersDB.create_collection(USERS_COL_NAME, validator={
        '$jsonSchema': {
            'oneOf': [
                {
                    'bsonType': 'object',
                    'required': ['uid', 'setup', 'guest'],
                    'additionalProperties': False,
                    'properties': {
                        '_id': { 'bsonType': 'objectId' },
                        'uid': {
                            'bsonType': 'string',
                            'description': 'unique user id of the user'
                        },
                        'setup': { 'enum': [False] },
                        'guest': { 'bsonType': 'bool' },
                    }
                },
                {
                    'bsonType': 'object',
                    'required': ['uid', 'setup', 'guest', 'degree', 'planner', 'courses', 'settings'],
                    'additionalProperties': False,
                    'properties': {
                        '_id': { 'bsonType': 'objectId' },
                        'uid': {
                            'bsonType': 'string',
                            'description': 'unique user id of the user'
                        },
                        'setup': { 'enum': [True] },
                        'guest': { 'bsonType': 'bool' },
                        'degree': {
                            'bsonType': 'object',
                            'required': ['programCode', 'specs'],
                            'additionalProperties': False,
                            'properties': {
                                'programCode': {
                                    'bsonType': 'string',
                                    'description': 'the code of program taken'
                                },
                                'specs': {
                                    'bsonType': 'array',
                                    'description': 'an array of all the specialisations taken',
                                    'items': {
                                        'bsonType': 'string'
                                    }
                                },
                            }
                        },
                        'courses': {
                            'bsonType': 'object',
                            'description': 'an object of CourseCode -> CourseInformation mapping',
                            'properties': {},
                            'additionalProperties': {
                                'bsonType': 'object',
                                'required': ['code', 'mark', 'uoc', 'ignoreFromProgression'],
                                'additionalProperties': False,
                                'properties': {
                                    'code': {
                                        'bsonType': 'string',
                                        'description': 'Course code repeated',
                                    },
                                    'mark': {
                                        'oneOf': [
                                            { 'enum': ['SY', 'FL', 'PS', 'CR', 'DN', 'HD'] },
                                            { 'bsonType': ['int', 'null'] },
                                        ],
                                        'description': 'Mark entered for this course'
                                    },
                                    'uoc': {
                                        'bsonType': 'int',
                                        'description': 'UOC of this course',
                                    },
                                    'ignoreFromProgression': {
                                        'bsonType': 'bool',
                                        'description': 'Whether the course is ignored from progression checking',
                                    }
                                }
                            }
                        },
                        'planner': {
                            'bsonType': 'object',
                            'required': ['unplanned', 'startYear', 'isSummerEnabled', 'years', 'lockedTerms'],
                            'additionalProperties': False,
                            'properties': {
                                'lockedTerms': {
                                    'bsonType': 'object',
                                    'properties': {},
                                    'additionalProperties': { 'bsonType': 'bool' },
                                    'description': 'A map of <YEAR><TERM> -> boolean of which terms are locked. Example: 2024T1 -> True',
                                },
                                'unplanned': {
                                    'bsonType': 'array',
                                    'items': {
                                        'bsonType': 'string'
                                    }
                                },
                                'startYear': {
                                    'bsonType': 'int'
                                },
                                'isSummerEnabled': {
                                    'bsonType': 'bool'
                                },
                                'years': {
                                    'bsonType': 'array',
                                    'items': {
                                        'bsonType': 'object',
                                        'required': ['T0', 'T1', 'T2', 'T3'],
                                        'additionalProperties': False,
                                        'properties': {
                                            'T0': {
                                                'bsonType': 'array',
                                                'items': {
                                                    'bsonType': 'string'
                                                }
                                            },
                                            'T1': {
                                                'bsonType': 'array',
                                                'items': {
                                                    'bsonType': 'string'
                                                }
                                            },
                                            'T2': {
                                                'bsonType': 'array',
                                                'items': {
                                                    'bsonType': 'string'
                                                }
                                            },
                                            'T3': {
                                                'bsonType': 'array',
                                                'items': {
                                                    'bsonType': 'string'
                                                }
                                            }
                                        }
                                    },
                                }
                            }
                        },
                        'settings': {
                            'bsonType': 'object',
                            'required': ['showMarks', 'hiddenYears'],
                            'additionalProperties': False,
                            'properties': {
                                'showMarks': {
                                    'bsonType': 'bool',
                                    'description': 'Whether to show marks in the Term Planner'
                                },
                                'hiddenYears': {
                                    'bsonType': 'array',
                                    'items': {
                                        'bsonType': 'int'
                                    },
                                    'description': 'Indexes of years hidden in the Term Planner, 0 is startYear',
                                    'uniqueItems': True
                                }
                            }
                        }
                    }
                }
            ]
        }
    })

    usersDB[USERS_COL_NAME].create_index("uid", unique=True, name=UID_INDEX_NAME)

    # TODO: add later when we actually have a use for it, otherwise right now its just added pain
    # 'info': {
    #     'bsonType': 'object',  # placeholder for future, not sure what this shape will be
    #     'description': 'Any extra information gathered about the user, such as name'
    # },

def _create_refresh_tokens_collection():
    # refreshTokens {
    #     tok! string,     // unique indexed
    #     sid! uuid,       // indexed
    #     expiresAt! Date, // ttl indexed
    # }
    usersDB.create_collection(REFRESH_TOKENS_COL_NAME, validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['token', 'sid', 'expiresAt'],
            'additionalProperties': False,
            'properties': {
                '_id': { 'bsonType': 'objectId' },
                'token': {
                    'description': 'The refresh token associated with a user session',
                    'bsonType': 'string',
                },
                'sid': {
                    'description': 'Session ID - UUID',
                    'bsonType': 'binData',
                },
                'expiresAt': {
                    'description': 'Expiry time of this refresh token document',
                    'bsonType': 'date',
                },
            }
        }
    })

    usersDB[REFRESH_TOKENS_COL_NAME].create_index("expiresAt", expireAfterSeconds=0)
    usersDB[REFRESH_TOKENS_COL_NAME].create_index("token", unique=True, name=TOKEN_INDEX_NAME)
    usersDB[REFRESH_TOKENS_COL_NAME].create_index("sid", name=SID_INDEX_NAME)

def _create_sessions_collection():
    # sessions {
    #     sid! uuid,       // unique indexed
    #     uid! string,     // index on if we dont have the reverse lookup
    #     expiresAt! Date, // ttl indexed (should be same as the currRefTok expiry time, or +1 day)
    #     type! notsetup | csesoc | guest,
    #     currRefTok? string,
    #     oidcInfo? {
    #         access_token string         # most recent access token
    #         raw_id_token string         # most recent id token string
    #         refresh_token string        # most recent refresh token
    #         validated_id_token: object  # most recent valid id token object,
    #     },
    # }
    usersDB.create_collection(SESSIONS_COL_NAME, validator={
        '$jsonSchema': {
            'oneOf': [
                {
                    'bsonType': 'object',
                    'required': ['sid', 'uid', 'currRefreshToken', 'oidcInfo', 'expiresAt', 'type'],
                    'additionalProperties': False,
                    'properties': {
                        '_id': { 'bsonType': 'objectId' },
                        'sid': {
                            'description': 'Session ID - UUID',
                            'bsonType': 'binData',
                        },
                        'uid': {
                            'description': 'User ID',
                            'bsonType': 'string',
                        },
                        'currRefreshToken': {
                            'description': 'For protection against replay attacks',
                            'bsonType': 'string',
                        },
                        'oidcInfo': {
                            'description': 'The required oidc tokens for refreshing',
                            'bsonType': 'object',
                            'required': ['accessToken', 'refreshToken', 'rawIdToken', 'validatedIdToken'],
                            'additionalProperties': False,
                            'properties': {
                                'accessToken': { 'bsonType': 'string' },
                                'refreshToken': { 'bsonType': 'string' },
                                'rawIdToken': { 'bsonType': 'string' },
                                'validatedIdToken': { 'bsonType': 'object' },
                            },
                        },
                        'expiresAt': {
                            'description': 'Expiry time of this session document',
                            'bsonType': 'date',
                        },
                        'type': { 'enum': ['csesoc'] },
                    },
                },
                {
                    'bsonType': 'object',
                    'required': ['sid', 'uid', 'currRefreshToken', 'expiresAt', 'type'],
                    'additionalProperties': False,
                    'properties': {
                        '_id': { 'bsonType': 'objectId' },
                        'sid': {
                            'description': 'Session ID - UUID',
                            'bsonType': 'binData',
                        },
                        'uid': {
                            'description': 'User ID',
                            'bsonType': 'string',
                        },
                        'currRefreshToken': {
                            'description': 'For protection against replay attacks',
                            'bsonType': 'string',
                        },
                        'expiresAt': {
                            'description': 'Expiry time of this session document',
                            'bsonType': 'date',
                        },
                        'type': { 'enum': ['guest'] },
                    },
                },
                {
                    'bsonType': 'object',
                    'required': ['sid', 'uid', 'expiresAt', 'type'],
                    'additionalProperties': False,
                    'properties': {
                        '_id': { 'bsonType': 'objectId' },
                        'sid': {
                            'description': 'Session ID - UUID',
                            'bsonType': 'binData',
                        },
                        'uid': {
                            'description': 'User ID',
                            'bsonType': 'string',
                        },
                        'expiresAt': {
                            'description': 'Expiry time of this session document',
                            'bsonType': 'date',
                        },
                        'type': { 'enum': ['notsetup'] },
                    },
                },
            ]
        }
    })

    usersDB[SESSIONS_COL_NAME].create_index("expiresAt", expireAfterSeconds=0)
    usersDB[SESSIONS_COL_NAME].create_index("sid", unique=True, name=SID_INDEX_NAME)
    usersDB[SESSIONS_COL_NAME].create_index("uid", name=UID_INDEX_NAME)

def _overwrite_main_collection(collection_name):
    """Overwrites the specific core database via reading from the json files.
    Collection names can be: Programs, Specialisations, Courses"""
    file_name = FINAL_DATA_PATH + collection_name.lower() + "Processed.json"

    with open(file_name, encoding="utf8") as f:
        try:
            db[collection_name].drop()

            file_data = json.load(f)
            for key in file_data:
                db[collection_name].insert_one(file_data[key])

            print(f"Finished overwriting {collection_name}")
        except (KeyError, IOError, OSError):
            print(f"Failed to load and overwrite {collection_name}")


def _overwrite_archives():
    """Overwrite all the archived data for all the years that we have archived"""
    for year in ARCHIVED_YEARS:
        file_name = ARCHIVED_DATA_PATH + str(year) + ".json"

        with open(file_name, encoding="utf8") as f:
            try:
                archivesDB[str(year)].drop()

                file_data = json.load(f)
                for key in file_data:
                    archivesDB[str(year)].insert_one(file_data[key])

                print(f"Finished overwriting {year} archive")
            except (KeyError, IOError, OSError):
                print(f"Failed to load and overwrite {year} archive")


def setup_user_related_collections(drop: bool):
    """Sets up all the user related collections to store users, refresh tokens and sessions"""
    # tear down if needed
    if drop:
        print("Dropping user and session related collections")
        usersDB.drop_collection(USERS_COL_NAME)
        usersDB.drop_collection(REFRESH_TOKENS_COL_NAME)
        usersDB.drop_collection(SESSIONS_COL_NAME)
    else:
        # try prevent any mismatches of data if not dropped (probably over the top but just in case)
        existing = usersDB.list_collection_names()
        if USERS_COL_NAME not in existing and (REFRESH_TOKENS_COL_NAME in existing or SESSIONS_COL_NAME in existing):
            # make sure there are no sessions or refresh tokens alive that could be pointing to non existent users
            print("Dropping session related collections because users was not present...")
            usersDB.drop_collection(REFRESH_TOKENS_COL_NAME)
            usersDB.drop_collection(SESSIONS_COL_NAME)

        if SESSIONS_COL_NAME not in existing and REFRESH_TOKENS_COL_NAME in existing:
            # dont want any refresh tokens that point to non existent sessions
            print("Dropping refresh tokens because it was present without sessions...")
            usersDB.drop_collection(REFRESH_TOKENS_COL_NAME)

    # build up
    # TODO: setup data versioning so we migrate shapes if needed
    existing = usersDB.list_collection_names()
    if USERS_COL_NAME not in existing:
        _create_users_collection()

    if SESSIONS_COL_NAME not in existing:
        _create_sessions_collection()

    if REFRESH_TOKENS_COL_NAME not in existing:
        _create_refresh_tokens_collection()

    print("Finished setting up user database")


def overwrite_all_static_data():
    """Singular execution point to overwrite the entire main database including the archives"""
    _overwrite_main_collection(COURSES_COL_NAME)
    _overwrite_main_collection(SPECS_COL_NAME)
    _overwrite_main_collection(PROGRAMS_COL_NAME)
    _overwrite_archives()


def setup_mongo_collections(clear_users=False):
    """Main function to setup all collections"""
    # TODO: setup smart overwrite of static data
    setup_user_related_collections(clear_users)
    overwrite_all_static_data()
