from fastapi import FastAPI
from server.routers import planner, courses, programs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    "http://frontend:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(planner.router)
app.include_router(courses.router)
app.include_router(programs.router)

@app.get('/')
async def index():
    return "At index inside server.py"
