""" run all of circles in one terminal, assuming a unix environment """

import os
import logging
import sys
import threading
from subprocess import run, Popen, check_call
from typing import TextIO
from dotenv import dotenv_values


# also crazy - autoconfigure the environment if it is borked
if not os.path.exists(".venv"):
    if run("./create_venv.sh", shell=True, check=False).returncode != 0:
        print("please follow the above instructions to set up venv correctly")
        sys.exit(1)

os.system(". .venv/bin/activate")


if run("npm --version", shell=True, check=False).returncode != 0:
    print("You must install npm. Please follow the onboarding instructions to install npm")
    sys.exit(1)

if not os.path.exists("frontend/node_modules"):
    run("cd frontend; npm install", shell=True, check=False)


class LogPipe(threading.Thread, TextIO):
    """ boilerplate abstraction for redirecting the logs of a process """
    # TODO: implement the abstract methods it is complaining about
    # pylint: disable=abstract-method
    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe"""
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything."""
        for line in iter(self.pipeReader.readline, ""):
            logging.log(self.level, line.strip("\n"))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe."""
        os.close(self.fdWrite)

    def write(self, message):
        """do write"""
        logging.log(self.level, message)


def get_backend_env() -> dict[str, str]:
    """
    Reads backend.env and merges it with a copy of the os environment.
    Also overwrites the database service names to be localhost, since the processes are running outside of the docker network.
    """
    res = os.environ.copy()
    res.update((k, v) for (k, v) in dotenv_values("./env/backend.env").items() if v is not None)
    res["MONGODB_SERVICE_HOSTNAME"] = "localhost"
    res["SESSIONSDB_SERVICE_HOSTNAME"] = "localhost"
    res["PYTHONUNBUFFERED"] = "1"  # this is necessary for the uvicorn worker to send through output

    return res

def get_frontend_env() -> dict[str, str]:
    """
    reads frontend.env and merges it with a copy of the os environment.
    """
    res = os.environ.copy()
    res.update((k, v) for (k, v) in dotenv_values("./env/frontend.env").items() if v is not None)

    return res


def main():
    if os.system("docker ps > /dev/null") != 0:
        print("please run docker first!")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        handlers=[logging.FileHandler("debug.log", mode="w"), logging.StreamHandler()],
    )
    # this is actually kooky if you think about it
    sys.stdout = LogPipe(logging.INFO)
    sys.stderr = LogPipe(logging.ERROR)

    backend_env = get_backend_env()
    frontend_env = get_frontend_env()
    python_ver = backend_env.get("PYTHON_VERSION", "python")

    os.system("docker compose up -d sessionsdb mongodb")

    try:
        # pylint: disable=consider-using-with
        Popen(
            f"{python_ver} -u runserver.py --dev",
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
            cwd="backend/",
            env=backend_env,
        )

        check_call(
            "npm start",
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
            cwd="frontend/",
            env=frontend_env,
        )
    except Exception as e:
        sys.stdout.write(f"exception - {e}")
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logging.shutdown()


if __name__ == "__main__":
    main()
