import json
import re
import sys
'''HELPER FUNCTIONS TO DETERMINE THE TYPE OF A GIVEN TEXT'''

def is_course(text) -> bool:
    return bool(re.match(r'^[A-Z]{4}\d{4}$', text, flags=re.IGNORECASE))


def is_uoc(text) -> bool:
    '''If the text is UOC'''
    return bool(re.match(r'^\d+UOC$', text, flags=re.IGNORECASE))


def get_uoc(text: str) -> int:
    '''Given a text in the format of ???UOC, will extract the uoc and return as an int'''
    return int(re.match(r'^(\d+)UOC$', text, flags=re.IGNORECASE).group(1))


def is_wam(text) -> bool:
    '''If the text is WAM'''
    return bool(re.match(r'^\d+WAM$', text, flags=re.IGNORECASE))

def get_wam(text):
    '''Given a text in the format of ???WAM, will extract the wam and return as a int'''
    return int(re.match(r'^(\d+)WAM$', text, flags=re.IGNORECASE).group(1))


def is_grade(text):
    '''If the text is GRADE'''
    return bool(re.match(r'^\d+GRADE$', text, flags=re.IGNORECASE))


def get_grade(text):
    '''Given a text in the format of ???GRADE, will extract the grade and return as a int'''
    return int(re.match(r'^(\d+)GRADE$', text, flags=re.IGNORECASE).group(1))


def is_program(text):
    '''Determines if the text is a program code'''
    return bool(re.match(r'^\d{4}$', text) or re.match(r'^[A-Z]{5}\d{5}', text) or re.match(r'^[A-Z]{6}\d{4}', text))

def is_program_type(program: str):
    return bool(re.match(r'^[A-Z]{4}#$', program, flags=re.IGNORECASE))

def is_specialisation(text):
    '''Determines if the text is a specialisation code'''
    return bool(re.match(r'^[A-Z]{5}\d$', text, flags=re.IGNORECASE))


'''HELPER FUNCTIONS FOR UTILITY PURPOSES'''


def read_data(file_name):
    '''Reads data from a json file and returns it'''
    try:
        with open(file_name, "r") as input_file:
            return json.load(input_file)
    except:
        print(f"File {file_name} not found")
        sys.exit(1)