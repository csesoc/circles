""" The central point from where we will run our server. It will open up the
api and also run the files"""

import argparse
import sys

import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite-course-data",
        action="store_true",
        help="Inclusion of option will force overwrite the courses database",
    )
    parser.add_argument(
        "--overwrite-all-data",
        action="store_true",
        help="Inclusion of option will force overwrite the entire database (including users)",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Inclusion of option will enable hot-reloading and smart-overwrite"
    )

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        sys.exit(0)

    print(
        "-- Running server with CLI options:",
        ", ".join(f"{k}={v}" for k, v in vars(args).items())
    )
    if args.overwrite_course_data or args.overwrite_all_data or args.dev:
        # TODO-OLLI(pm): abstract this, and remove these local imports once we have proper connection handling
        # TODO-OLLI(pm): also do overwrite checks for dev mode using a timestamp
        # TODO-OLLI: dont we always want to atleast setup the dbs???
        from server.db.mongo.setup import setup_mongo_collections
        from server.db.redis.setup import setup_redis_sessionsdb

        setup_mongo_collections(clear_users=args.overwrite_all_data)
        print(f"-- Finished Mongo Setup (drop users={args.overwrite_all_data})")

        setup_redis_sessionsdb()
        print("-- Finished Redis Setup")

    print(f"-- Starting uvicorn(reload={args.dev})")
    uvicorn.run(
        "server.server:app",
        host='0.0.0.0',
        lifespan="on",
        reload=args.dev,
        reload_excludes="*.json" if args.dev else None,
    )
