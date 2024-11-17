from typing import cast

from fastapi import HTTPException
from data.processors.models import SpecData
from server.routers.model import SpecType
from server.routers.utility.common import get_all_specialisations


def validate_degree(programCode: str, specs: list[str]):
    # Ensure that all specialisations are valid
    # Need a bidirectional validate
    # All specs in wizard (lhs) must be in the RHS
    # All specs in the RHS that are "required" must have an associated LHS selection

    # Keys in the specInfo
    # - 'specs': List[str] - name of the specialisations - thing that matters
    # - 'notes': str - dw abt this (Fe's prob tbh)
    # - 'is_optional': bool - if true then u need to validate associated elem in LHS

    possible_specs = get_all_specialisations(programCode)
    if possible_specs is None:
        raise HTTPException(status_code=400, detail="Invalid program code")

    # list[(is_optional, spec_codes)]
    flattened_containers: list[tuple[bool, list[str]]] = [
        (
            program_sub_container["is_optional"],
            list(program_sub_container["specs"].keys())
        )
        for spec_type_container in cast(dict[SpecType, dict[str, SpecData]], possible_specs).values()
        for program_sub_container in spec_type_container.values()
    ]

    invalid_lhs_specs = set(specs).difference(
        spec_code
        for (_, spec_codes) in flattened_containers
        for spec_code in spec_codes
    )

    spec_reqs_not_met = any(
        (
            not is_optional
            and not set(spec_codes).intersection(specs)
        )
        for (is_optional, spec_codes) in flattened_containers
    )

    # Doesn't return what is wrong, assuming Wizard/import will be valid
    if invalid_lhs_specs or spec_reqs_not_met:
        raise HTTPException(status_code=400, detail="Invalid specialisations")
