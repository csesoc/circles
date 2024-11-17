# Sets up the backend, opening it to reload on change
# Python image
FROM python:3.12.3-slim

# Set current working directory inside container to /backend
WORKDIR /backend

# pip install the venv python modules
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# At time of writing this, uvicorn reload wouldn't pass through stdout
# https://testdriven.io/blog/fastapi-docker-traefik/
# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run the server
# https://forums.docker.com/t/docker-run-cannot-be-killed-with-ctrl-c/13108/2
ENTRYPOINT ["python3", "-u", "runserver.py", "--dev"]
