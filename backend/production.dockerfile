# Sets up the backend, without writing data into the database.

# Python image
FROM python:3.12.3-slim

# gcc required for python-Levenshtein, curl required for healthcheck
RUN apt-get update \
    && apt-get install gcc curl -y \
    && apt-get clean

# Set current working directory inside container to /backend
WORKDIR /backend

# pip install the venv python modules
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the server
ENTRYPOINT ["python3", "-u", "runserver.py", "--overwrite-course-data"]
