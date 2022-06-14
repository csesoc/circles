# we want to assure that courses that may be accessed from a container are always accurately computed.
from contextlib import suppress
import requests

from server.tests.courses.test_getAllUnlocked import USERS

ignored = ['ECON2209', 'ECON2112', 'ECON2101', 'ECON2102']

def test_validation_majors():
    unlocked = requests.post('http://127.0.0.1:8000/courses/getAllUnlocked', json=USERS["user3"]).json()['courses_state']
    for program in requests.get('http://127.0.0.1:8000/programs/getPrograms').json()['programs']:
        majorsGroups = requests.get(f'http://127.0.0.1:8000/programs/getMajors/{program}').json()['majors']
        for group in majorsGroups.values():
            for major in group["specs"].keys():
                assert_possible_structure(unlocked, program, major)

def test_validation_minors():
    unlocked = requests.post('http://127.0.0.1:8000/courses/getAllUnlocked', json=USERS["user3"]).json()['courses_state']
    for program in requests.get('http://127.0.0.1:8000/programs/getPrograms').json()['programs']:
        majorGroups = requests.get(f'http://127.0.0.1:8000/programs/getMajors/{program}').json()['majors']
        minorGroups = requests.get(f'http://127.0.0.1:8000/programs/getMinors/{program}').json()['minors']
        for majGroup in majorGroups.values():
            for major in majGroup["specs"].keys():
                for group in minorGroups.values():
                    for minor in group["specs"].keys():
                        assert_possible_structure(unlocked, program, major, minor)


def assert_possible_structure(unlocked, program, major, minor = ''):
    structure = requests.get(f'http://127.0.0.1:8000/programs/getStructure/{program}/{major}/{minor}').json()['structure']
    for container in structure:
        with suppress(KeyError):
            del structure[container]['name']
            del structure[container]['Flexible Education']
            del structure[container]['General Education']
            del structure[container]['Prescribed Work Integrated Learning (WIL) Course']
            del structure[container]['Integrated First Year Courses']
            del structure[container]['Final Year Synthesis']
            del structure[container]['myBCom']
            del structure[container]['Compulsory Core']

        for container2 in structure[container]:
            with suppress(KeyError):
                del structure[container][container2]['name']

                for course in structure[container][container2]['courses']:
                    for c in unlocked:
                        if course in c and c not in ignored:
                            assert unlocked[c]['is_accurate'], f"{c} is inaccurate"
