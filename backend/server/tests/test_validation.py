# we want to assure that courses that may be accessed from a container are always accurately computed.
from contextlib import suppress
from itertools import chain
import json
from typing import Any
import pytest
import requests
from server.routers.model import StructureContainer
from server.tests.programs.test_get_structure import fake_specs

with open("./algorithms/tests/exampleUsers.json", encoding="utf8") as f:
    USERS = json.load(f)

FAILS: list[Any] = []

# TODO: some of these should probs not be ignored
ignored = [
    'ARCH1101', 'ADAD4100', 'ARTS3', 'AVIA2117', 'BABS3021', 'BEES', 'BEIL6',
    'BENV6713', 'BIOC3', 'BIOM4951', 'BIOS3161', 'BLDG', 'CDEV3101',
    'CODE3100', 'CEIC', 'CRIM2021', 'CRIM3', 'CVEN4701', 'DART2151',
    'CHEM2521', 'DATA3001', 'DP', 'EDST6716', 'EDST6761', 'EDST6771',
    'GMAT4061', 'HESC3541', 'HUMS1007', 'LAWS', 'MDIA', 'MICR3621', 'MMAN4951',
    'MUSC', 'NEUR2201', 'PHAR2011', 'PHAR3102', 'PHAR3251', 'PHCM1001',
    'PHSL','3199', '3299', 'SDES', 'SOCW', 'SOLA49', 'SOSS', 'SRAP',
    'ZHSS3501', 'FOOD6804', 'PATH3209', 'SOMS', 'YMED',
    # 'LAND1351', "MFAC1526",
    # "LAND1351", "SCIF1000", "MFAC1501", "COMM1140", "MFAC1524", "MFAC1527",
    # "ANAT1452", "MFAC1525", "MFAC1522", "COMM1120", "MFAC1521", "MFAC1523",
    # "FINS3647", "ACTL3143", "COMM3000", 'CHEM4508', 'PHYS3118', 'AVIA2225',
    # 'AVIA3025', 'CHEM4516', 'PHYS2116', 'BIOS3171', 'AVIA2125'
]

@pytest.mark.skip(reason="takes too long; too extensive; manual sanity check close enough")
def test_validation():
    unlocked = requests.post('http://127.0.0.1:8000/courses/getAllUnlocked', json=USERS['user3']).json()['courses_state']
    for program in requests.get('http://127.0.0.1:8000/programs/getPrograms').json()['programs']:
        majorsGroups = requests.get(f'http://127.0.0.1:8000/specialisations/getSpecialisations/{program}/majors')
        minorsGroups = requests.get(f'http://127.0.0.1:8000/specialisations/getSpecialisations/{program}/minors')
        honoursGroups = requests.get(f'http://127.0.0.1:8000/specialisations/getSpecialisations/{program}/honours')
        majorsGroups = majorsGroups.json()['spec'] if majorsGroups.status_code == 200 else {}
        minorsGroups = minorsGroups.json()['spec'] if minorsGroups.status_code == 200 else {}
        honoursGroups = honoursGroups.json()['spec'] if honoursGroups.status_code == 200 else {}
        for group in chain(majorsGroups.values(), minorsGroups.values(), honoursGroups.values()):
            for spec in group['specs'].keys():
                if spec not in fake_specs:
                    assert_possible_structure(unlocked, program, spec)

    assert FAILS == [], f"Failed possible structure tests: {FAILS}"


def assert_possible_structure(unlocked, program, spec):
    structure: dict[str,StructureContainer] = requests.get(f'http://127.0.0.1:8000/programs/getStructure/{program}/{spec}').json()['structure']
    failed_set = set()
    for container in structure:
        with suppress(KeyError):
            del structure[container]['content']['General Education']
        for container2 in structure[container]['content']:
            for structure_course in structure[container]['content'][container2]['courses']:
                for unlocked_course in unlocked:
                    is_accurate = unlocked[unlocked_course]['is_accurate']
                    is_ignored = any(ignore_term in unlocked_course for ignore_term in ignored)
                    if structure_course in unlocked_course and not is_ignored and not is_accurate:
                        # print(
                        #     "Failing Possible Structure:"
                        #     f"\n\tC: {unlocked_course}"
                        #     f"\n\tCourse: {structure_course}"
                        #     f"\n\tUnlocked: {unlocked[unlocked_course]}"
                        # )
                        failed_set.add(unlocked_course)
    if failed_set.__len__() > 0:
        FAILS.append((program, spec, failed_set))
    # assert len(failed_set) == 0, f'courses: {failed_set} are inaccurate for program: {program}, spec: {spec}'
