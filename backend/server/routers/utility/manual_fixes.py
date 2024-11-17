from contextlib import suppress

from server.routers.model import StructureContainer


def remove_course(structure: dict[str, StructureContainer], course: str):
    """indescriminantly remove a course from structure"""
    for item, collection in structure.items():
        if item == "Rules":
            continue
        for container in collection["content"]:
            try:
                del structure[item]["content"][container]["courses"][course]
                return structure[item]
            except KeyError:
                pass
    return None

def fix_3784(structure: dict[str, StructureContainer]):
    mutated_item = remove_course(structure, "ECON1202")
    if mutated_item:
        with suppress(StopIteration):
            core_name = next(filter(lambda a: "core" in a.lower(), mutated_item.keys()))
            mutated_item[core_name]["UOC"] -= 6
            elective_name = next(filter(lambda a: "prescribed" in a.lower(), mutated_item.keys()))
            mutated_item[elective_name]["UOC"] += 6
    return structure

def fix_3673(structure: dict[str, StructureContainer]):
    mutated_item = remove_course(structure, "ECON1202")
    if mutated_item:
        with suppress(StopIteration):
            core_name = next(filter(lambda a: "core" in a.lower(), mutated_item['content'].keys()))
            mutated_item['content'][core_name]["UOC"] -= 6

    mutated_item = remove_course(structure, "ECON1203")
    if mutated_item:
        with suppress(StopIteration):
            core_name = next(filter(lambda a: "core" in a.lower(), mutated_item['content'].keys()))
            mutated_item['content'][core_name]["UOC"] -= 6

    return structure

def fix_3785(structure: dict[str, StructureContainer]):
    remove_course(structure, "COMP1911")
    remove_course(structure, "ENGG1811")

    # eject 1081 from CS
    with suppress(StopIteration, KeyError):
        comp_major = next(filter(lambda a: "COMP" in a, structure.keys()))
        core_name = next(filter(lambda a: "core" in a.lower(), structure[comp_major]["content"].keys()))
        del structure[comp_major]["content"][core_name]["courses"]["MATH1081"]

    mutated_item = remove_course(structure, "COMP4920")
    if mutated_item:
        with suppress(StopIteration):
            core_name = next(filter(lambda a: "core" in a.lower(), mutated_item.keys()))
            mutated_item[core_name]["UOC"] -= 12
    return structure

def apply_manual_fixes(structure: dict[str, StructureContainer], program_code: str):
    fixes = {
        "3784": fix_3784,
        "3785": fix_3785,
        "3673": fix_3673,
    }
    return fixes.get(program_code, lambda a: a)(structure)
