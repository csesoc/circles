import requests
from pytest import mark

from server.tests.user.utility import clear, get_token, get_token_headers


@mark.skip(reason = "Autoplanning incompatiable with migration")
def test_autoplanning_generic():
    clear()
    token = get_token()
    headers = get_token_headers(token)
    requests.put('http://127.0.0.1:8000/user/import', json={
        "degree": {
            "programCode": "3778",
            "specs": [
                "COMPA1"
            ]
        },
        "planner": {
            "years": [ 
                {
                    "T0": [],
                    "T1": [],
                    "T2": [],
                    "T3": []
                },
                {
                    "T0": [],
                    "T1": [],
                    "T2": [],
                    "T3": []
                },
                {
                    "T0": [],
                    "T1": [],
                    "T2": [],
                    "T3": []
                },
                {
                    "T0": [],
                    "T1": [],
                    "T2": [],
                    "T3": []
                }
            ],
            "unplanned": [],
            "startYear": 2020,
            "isSummerEnabled": False,
            "lockedTerms": {}
        }
    }, headers=headers)

    x = requests.post(
        'http://127.0.0.1:8000/planner/autoplanning', json={
            'courseCodes': [
                'COMP1511', 'COMP2521', 'COMP1531', 'COMP1521', 'MATH1141', 'MATH1241', 'MATH1081', 'COMP2041', 'ENGG2600', 'ENGG2600', 'ENGG2600', 'COMP2511', 'MATH3411', 'COMP3411', 'COMP6841', 'COMP3231', 'COMP3141', 'COMP3121', 'COMP3131', 'COMP4141', 'COMP3901', 'ARTS1360'
            ],
            'programTime': {
                'startTime': [2020, 1],
                'endTime': [2023, 3],
                'uocMax': [
                    12, 20, 20, 20, 12, 20, 20, 20, 10, 20, 20, 20, 10, 20, 20, 20
                ]
            },
        },
        headers=headers
    )
    assert x.status_code == 200
    # TODO: please write actual tests
