"""
Testing functionality related to general education units.
"""

from typing import List

import requests


def test_get_gened_no_overlap():
    """
    Tests that the gened list returned for a given program has no over-lap with
    ... TODO:
    """

    no_geneds: List[str] = []

    program_res = requests.get('http://127.0.0.1:8000/programs/getAllPrograms')
    assert program_res.status_code == 200
    programs = program_res.json()['programs']

    # the intersection between the gened list for a given program and the
    # course list generated from getStructure should be empty
    for program_code in programs.keys():

        geneds_res = requests.get(f'http://127.0.0.1:8000/programs/getGenEds/{program_code}')

        # We don't care if geneds are not found for all programs
        if geneds_res.status_code == 400:
            no_geneds.append((program_code, geneds_res.status_code))
            continue

        assert geneds_res.status_code == 200
        geneds = geneds_res.json()['courses']
        courses = requests.get(
            f"http://127.0.0.1:8000/programs/getStructureCourseList/{program_code}"
        ).json()["courses"]
        assert not set(geneds).intersection(set(courses))

    assert len(no_geneds) <= 35

    deployed_programs_res = requests.get('http://127.0.0.1:8000/programs/getAllPrograms')
    assert deployed_programs_res.status_code == 200
    deployed_programs = deployed_programs_res.json()['programs']

    # Cannot have failures for anything that is deployed
    assert set(no_geneds).intersection(set(deployed_programs.keys())) == set()

