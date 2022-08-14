""" Specialisations Route """
from typing import Literal, Optional, cast
from fastapi import APIRouter, HTTPException
from server.database import programsCOL, specialisationsCOL
from server.routers.model import SpecialisationTypes, Specialisations
from data.processors.models import Program

router = APIRouter(
    prefix="/specialisations",
    tags=["specialisations"],
)


@router.get("/")
def specialisations_index():
    """ sanity test that this file is loaded """
    return "Index of specialisations"

@router.get(
    "/getSpecialisationTypes/{programCode}",
    response_model=SpecialisationTypes,
    responses={
        200: {"types": ["majors", "minors"]}
    }
)
def get_specialisation_types(programCode):
    """ get the possible types of a program """
    result = programsCOL.find_one({"code": programCode})

    if not result:
        raise HTTPException(
            status_code=400, detail="Program code was not found")
    return {"types": [*result["components"]["spec_data"].keys()]}


@router.get(
    "/getSpecialisations/{programCode}/{typeSpec}",
    response_model=Specialisations,
    responses={
        400: {
            "description": "The given program code could not be found in the database",
        },
        200: {
            "description": "Returns all majors to the given code",
            "content": {
                "application/json": {
                    "example": {
                        "spec": {
                            "Computer Science": {
                                "specs": {
                                    "COMPS1": "Computer Science (Embedded Systems)",
                                    "COMPJ1": "Computer Science (Programming Languages)",
                                    "COMPE1": "Computer Science (eCommerce Systems)",
                                    "COMPA1": "Computer Science",
                                    "COMPN1": "Computer Science (Computer Networks)",
                                    "COMPI1": "Computer Science (Artificial Intelligence)",
                                    "COMPD1": "Computer Science (Database Systems)",
                                    "COMPY1": "Computer Science (Security Engineering)",
                                },
                                "note": "COMPA1 is the default stream, and will be used if no other stream is selected."
                            }
                        }
                    }
                }
            },
        },
    },
)
def get_specialisations(programCode: str, typeSpec: Literal["majors"] | Literal["minors"] | Literal["honours"]):
    """ Fetch all the majors known to the backend for a specific program """
    result = cast(Optional[Program], programsCOL.find_one({"code": programCode}))

    if not result:
        raise HTTPException(
            status_code=400, detail="Program code was not found")

    specRes = result["components"]["spec_data"].get(typeSpec)
    if not specRes:
        raise HTTPException(
            status_code=404, detail=f"this program has no {typeSpec}")

    for item in specRes.values():
        for code in [*item["specs"].keys()]:
            if not specialisationsCOL.find_one({"code": code}):
                del item["specs"][code]

    return {"spec": result["components"]["spec_data"][typeSpec]}
