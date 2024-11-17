# assumes that getPrograms, getMajors, and getMinors isnt borked.
import copy
import requests
from hypothesis import given, settings
from hypothesis.strategies import composite, sampled_from

programs = [
    *requests.get("http://127.0.0.1:8000/programs/getPrograms")
    .json()["programs"]
    .keys()
]
# this is stupid - this is because canberra has seperate degrees for these, and these arent offered in KENS
fake_specs = ["NAVLAH", "GMATEH", "ARCYB2"]

@composite
def major_minor_for_program(draw):
    possible_programs = copy.deepcopy(programs)
    # possible_programs.remove("3362") # City Planning (Honours) does not have majors/minors

    program = draw(sampled_from(possible_programs))
    possible_specs: list[str] = []
    for t in requests.get(f"http://127.0.0.1:8000/specialisations/getSpecialisationTypes/{program}").json()["types"]:
        majorsRequest = requests.get(f"http://127.0.0.1:8000/specialisations/getSpecialisations/{program}/{t}")
        majorsRequestJson = majorsRequest.json()['spec'] if majorsRequest.status_code == 200 else {}
        possible_specs.extend(sum((list(prog['specs'].keys()) for prog in majorsRequestJson.values()), []))


    # select doubles
    strat = sampled_from(possible_specs)
    spec1 = draw(strat)
    spec2 = draw(strat)
    while spec1 in fake_specs:
        spec1 = draw(strat)
    while spec2 in fake_specs:
        spec2 = draw(strat)
    return (program, spec1, spec2)


@given(sampled_from(programs))
@settings(deadline=5000)
def test_all_programs_fetched(program):
    structure = requests.get(f"http://127.0.0.1:8000/programs/getStructure/{program}")
    assert structure != 500
    assert structure.json()["structure"]["General"] != {}

@given(major_minor_for_program())
@settings(deadline=1500)
def test_all_specs_fetched(specifics):
    # this is stupid
    if specifics[1] == specifics[2]:
        return
    structure = requests.get(
        f"http://127.0.0.1:8000/programs/getStructure/{specifics[0]}/{specifics[1]}+{specifics[2]}"
    )
    structure.json()["structure"]["General"] != {}
    if specifics[1].endswith("1") or specifics[2].endswith("1"):
        key_to_fetch = next(k for k in structure.json()["structure"].keys() if "Major" in k)
        assert structure.json()["structure"][key_to_fetch] is not None
    if specifics[1].endswith("H") or specifics[2].endswith("H"):
        key_to_fetch = next(k for k in structure.json()["structure"].keys() if "Honours" in k)
        assert structure.json()["structure"][key_to_fetch] is not None
    if specifics[1].endswith("2") or specifics[2].endswith("2"):
        key_to_fetch = next(k for k in structure.json()["structure"].keys() if "Minor" in k)
        assert structure.json()["structure"][key_to_fetch] is not None
