import os
import redis

sdb: redis.Redis

def connect():
    # TODO-OLLI(pm): make this not use ft.search and use our own secondary index
    global sdb
    print("Trying to connect to sessions db.")

    # should throw an error, better than exit(1)
    sdb = redis.Redis(
        host=os.environ["SESSIONSDB_SERVICE_HOSTNAME"],
        port=6379,
        protocol=3,
        decode_responses=True,
        username=os.environ["SESSIONSDB_USERNAME"],
        password=os.environ["SESSIONSDB_PASSWORD"]
    )
    print('Connected to sessions database.', sdb.ping())


# TODO-OLLI(pm): call this in the fastapi lifetime function
connect()
