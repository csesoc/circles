# Backend

### Installing Docker

Circles uses `docker` for development. This means you do not need to install anything locally on your machine and it avoids the hassle of configuring MongoDB locally. You will only need to install `docker` on your local system: `https://www.docker.com/get-started`.

We use docker to build 'images' for the backend, frontend, redis, and mongodb. These `images` can then be used to run `containers`. An image is a blueprint for a container and a container contains everything we need to run an application. All dependencies for code exist within these containers, and via `docker-compose`, these containers can talk to each other.

### Creating Environment Variables

#### NEW: Short way

You can now run the `setup_env.py` script to setup your env files automatically (it will prompt you every step of the way)!

#### Long way

MongoDB, redis and the backend require a few environment variables to get started. In the root folder, create a folder called `env` and add three files: `backend.env`, `sessionsdb.env`, `mongodb.env` and `frontend.env`. 

In `backend.env`, add the environment variables:

- `MONGODB_USERNAME=name`
- `MONGODB_PASSWORD=name`
- `MONGODB_SERVICE_HOSTNAME=mongodb`
- `SESSIONSDB_USERNAME=name`
- `SESSIONSDB_PASSWORD=name`

wherever you see "name", the value is not actually important.

FOR **PRODUCTION**, also add:
- `AUTH_CSE_CLIENT_SECRET=********` (redacted, contact CSE or one of the faculty societies for this secret)
- `AUTH_CSE_CLIENT_ID=********` (redacted, contact CSE or one of the faculty societies for this secret)
- `FORWARDED_ALLOW_IPS=*`

In `mongodb.env`, add:

- `MONGO_INITDB_ROOT_USERNAME=name` (must match `MONGODB_USERNAME` in `backend.env`)
- `MONGO_INITDB_ROOT_PASSWORD=name` (must match `MONGODB_PASSWORD` in `backend.env`)

In `sessionsdb.env`, add:

- `REDIS_USERNAME=peedee` (must match `SESSIONSDB_USERNAME` in `backend.env`)
- `REDIS_PASSWORD=peedee` (must match `SESSIONSDB_PASSWORD` in `backend.env`)
- `REDIS_ARGS="--user ${REDIS_USERNAME} on >${REDIS_PASSWORD} ~* allcommands"` (use this exactly, it uses your other two vars to make an admin user)

In `frontend.env`, add:

- `VITE_BACKEND_API_BASE_URL=http://localhost:8000/`

> NOTE: The `VITE_BACKEND_API_BASE_URL` environment variable is the base url endpoint that the backend is running on. If the environment variable is not specified, the react application will default to using `http://localhost:8000/` as the base url when calling the API endpoint.


You can use any random username and password wherever `name` has been used. The username and password in `backend.env` must match the values in `mongodb.env`, as indicated. The `env` folder has been added to `.gitignore` and will not be committed to the repo.

### Removing Docker Containers

To remove all containers and the docker network, run `docker-compose down`. Add the option `-v` to also remove persistent volumes: that is, the mongoDB and redis data. I tend to run this before I rebuild if I have made changes to the backend code to keep everything clean on my system.

To stop a docker containers that is running, run `docker-compose stop <containerName>`. This will not remove the container.

Every once in a while, you will want to clean up docker. To do this, use `docker compose prune`.
### Running Circles
#### Recommended: (kinda) without Docker
It is possible to run Circles without docker, to conserve system resources if it is taking too much of a toll. To do this, ensure you have the correct dependencies installed. This will require you to install the frontend dependencies using `npm i` and the backend dependencies using a **python virtual environment** (using venv or conda) and `python -m pip install -r backend/requirements.txt`. 
You can then run `python run_app.py` to run all of circles locally. MongoDB and Redis will still run under Docker, because they are external databases that you won't edit.
Ensure your python3 version is set toa t least 3.12. All parts of the app should now be running and talking to eachother. 

If you have having trouble with `python not found`, manually choose what python version is being run by adding `PYTHON_VERSION=python3` or, any version of your choosing in `backend.env`.
If you run into too many issues, you should use a complete docker solution, as below. This will be more power intensive to run, but is more likely to work without configuring your computer too much.

#### with docker
assuming that you correctly followed the steps above, you can run all of circles by using `docker compose up frontend` in a dev environment which will reflect your changes. If you change anything related to `database.py`, you will need to rebuild it to refect the changes.
