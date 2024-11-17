"""
Contains helper functions to assist with reading and writing data.
"""
import json
import sys


def read_data(file_name):
    """
    Reads file with given file_name and returns data
    """
    try:
        with open(file_name, "r", encoding="utf8") as INPUT_FILE:
            return json.load(INPUT_FILE)
    except (IOError, OSError):
        print(f"File {file_name} not found")
        sys.exit(1)


def write_data(data, file_name):
    """
    Writes a json dump of given data to file with given file_name
    """
    with open(file_name, "w", encoding="utf8") as OUTPUT_FILE:
        json.dump(data, OUTPUT_FILE, indent=4)
        print(f"{file_name} successfully created")
