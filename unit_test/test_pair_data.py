DB_DATA = [
    {
        "employee": [
            {
                "emp_email": "information@email.com",
                "emp_name": "Demonstration,Information",
                "emp_pref_name": "Demonstration,Information",
                "job_family": "Level 6",
                "job_level": 6,
                "pml_email": "",
                "pml_name": ""
            }
        ],
        "pml": [],
        "counsellee": [
            {
                "emp_email": "environment@email.com"
            },
            {
                "emp_email": "army@email.com"
            },
            {
                "emp_email": "potato@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [
            {
                "junior": "manager@email.com"
            }
        ],
    },
    {
        "employee": [
            {
                "emp_email": "environment@email.com",
                "emp_name": "Environment,Client",
                "emp_pref_name": "Environment,Client",
                "job_family": "Level 5",
                "job_level": 5,
                "pml_email": "information@email.com",
                "pml_name": "Demonstration,Information"
            }
        ],
        "pml": [
            {
                "emp_email": "information@email.com"
            }
        ],
        "counsellee": [
            {
                "emp_email": "marriage@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [],
    },
    {
        "employee": [
            {
                "emp_email": "army@email.com",
                "emp_name": "Army,Breath",
                "emp_pref_name": "Army,Breath",
                "job_family": "Level 4",
                "job_level": 4,
                "pml_email": "information@email.com",
                "pml_name": "Demonstration,Information"
            }
        ],
        "pml": [
            {
                "emp_email": "information@email.com"
            }
        ],
        "counsellee": [
            {
                "emp_email": "requirement@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [],
    },
    {
        "employee": [
            {
                "emp_email": "potato@email.com",
                "emp_name": "Potato,Fortune",
                "emp_pref_name": "Potato,Fortune",
                "job_family": "Level 3",
                "job_level": 3,
                "pml_email": "information@email.com",
                "pml_name": "Demonstration,Information"
            }
        ],
        "pml": [
            {
                "emp_email": "information@email.com"
            }
        ],
        "counsellee": [
            {
                "emp_email": "accident@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [],
    },
    {
        "employee": [
            {
                "emp_email": "marriage@email.com",
                "emp_name": "Marriage,City",
                "emp_pref_name": "Marriage,City",
                "job_family": "Level 2",
                "job_level": 2,
                "pml_email": "environment@email.com",
                "pml_name": "Environment,Client"
            }
        ],
        "pml": [
            {
                "emp_email": "environment@email.com"
            }
        ],
        "counsellee": [
            {
                "emp_email": "systematic@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [],
    },
    {
        "employee": [
            {
                "emp_email": "requirement@email.com",
                "emp_name": "Requirement,Device",
                "emp_pref_name": "Requirement,Device",
                "job_family": "Level 1",
                "job_level": 1,
                "pml_email": "army@email.com",
                "pml_name": "Army,Breath"
            }
        ],
        "pml": [
            {
                "emp_email": "army@email.com"
            }
        ],
        "counsellee": [
            {
                "emp_email": "student@email.com"
            }
        ],
        "junior_in_meeting": [],
        "senior_in_meeting": [],

    },
]


EXPECTED_POSSIBLE = [
    {
        "emp": {
            "emp_email": "information@email.com",
            "emp_name": "Demonstration,Information",
            "emp_pref_name": "Demonstration,Information",
            "job_family": "Level 6",
            "job_level": 6,
            "pml_email": "",
            "pml_name": ""
        },
        "invalid_match": {
            "environment@email.com",
            "army@email.com",
            "potato@email.com",
            "manager@email.com"
        }
    },
    {
        "emp": {
            "emp_email": "environment@email.com",
            "emp_name": "Environment,Client",
            "emp_pref_name": "Environment,Client",
            "job_family": "Level 5",
            "job_level": 5,
            "pml_email": "information@email.com",
            "pml_name": "Demonstration,Information"
        },
        "invalid_match": {
            "information@email.com",
            "marriage@email.com"
        }
    },
    {
        "emp": {
            "emp_email": "army@email.com",
            "emp_name": "Army,Breath",
            "emp_pref_name": "Army,Breath",
            "job_family": "Level 4",
            "job_level": 4,
            "pml_email": "information@email.com",
            "pml_name": "Demonstration,Information"
        },
        "invalid_match": {
            "information@email.com",
            "requirement@email.com"
        }
    },
    {
        "emp": {
            "emp_email": "potato@email.com",
            "emp_name": "Potato,Fortune",
            "emp_pref_name": "Potato,Fortune",
            "job_family": "Level 3",
            "job_level": 3,
            "pml_email": "information@email.com",
            "pml_name": "Demonstration,Information"
        },
        "invalid_match": {
            "information@email.com",
            "accident@email.com"
        }
    },
    {
        "emp": {
            "emp_email": "marriage@email.com",
            "emp_name": "Marriage,City",
            "emp_pref_name": "Marriage,City",
            "job_family": "Level 2",
            "job_level": 2,
            "pml_email": "environment@email.com",
            "pml_name": "Environment,Client"
        },
        "invalid_match": {
            "environment@email.com",
            "systematic@email.com"
    
        }
    },
    {
        "emp": {
            "emp_email": "requirement@email.com",
            "emp_name": "Requirement,Device",
            "emp_pref_name": "Requirement,Device",
            "job_family": "Level 1",
            "job_level": 1,
            "pml_email": "army@email.com",
            "pml_name": "Army,Breath"
        },
        "invalid_match": {
            "army@email.com",
            "student@email.com"
        }
    },
]


EXPECTED_EXISTING_CONNECTIONS = {
    "information@email.com": {
        "environment@email.com",
        "army@email.com",
        "potato@email.com",
        "manager@email.com"
    },
    "environment@email.com" : {
        "information@email.com",
        "marriage@email.com"
    },
    "army@email.com": {
        "information@email.com",
        "requirement@email.com"
    },
    "potato@email.com": {
        "information@email.com",
        "accident@email.com"
    },
    "marriage@email.com": {
        "environment@email.com",
        "systematic@email.com"
    },
    "requirement@email.com": {
        "army@email.com",
        "student@email.com"
    }
}


EXPECTED_LEVELLED = {
    6: {"information@email.com"},
    5: {"environment@email.com"},
    4: {"army@email.com"},
    3: {"potato@email.com"},
    2: {"marriage@email.com"},
    1: {"requirement@email.com"}
}
