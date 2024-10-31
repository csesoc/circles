"""
Configure the FastAPI server
"""

import os
from contextlib import asynccontextmanager
from data.config import LIVE_YEAR
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import auth, courses, followups, planner, programs, specialisations, user

@asynccontextmanager
async def on_setup_and_shutdown(_app: FastAPI):
    # TODO-OLLI(pm): actually use these
    print("\n\nstartup\n\n")
    yield
    print("\n\nshutdown\n\n")

app = FastAPI(lifespan=on_setup_and_shutdown)

origins = [
    "http://host.docker.internal",
    "http://host.docker.internal:8080",
    "http://host.docker.internal:8000",
    "http://host.docker.internal:3000",
    "http://host.docker.internal:3001",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://frontend",
    "http://frontend:8080",
    "http://frontend:8000",
    "http://frontend:3000",
    "http://frontend:3001",
    "https://circles.devsoc.app",
    "https://unilectives.devsoc.app",
    "https://unilectives.staging.devsoc.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(planner.router)
app.include_router(courses.router)
app.include_router(programs.router)
app.include_router(specialisations.router)
app.include_router(user.router)
app.include_router(followups.router)
# TODO: hide this behind a feature flag?
# app.include_router(ctf.router)
if os.getenv("ENV") == "dev":
    from server.routers import dev
    app.include_router(dev.router)


@app.get("/")
async def index() -> str:
    """sanity test that this file is loaded"""
    return "At index inside server.py"


@app.get("/live_year")
def live_year() -> int:
    """sanity check for the live year"""
    return LIVE_YEAR

@app.get("/ping")
def ping() -> str:
    """ping command useful for healthchecks"""
    return "pong"
