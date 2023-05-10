from app.settings import CONNECTION_RESET, MEETING_COLLECTION, ROSTER_COLLECTION

CONNECTIONS = [
    {"$match": {'iteration_name': '{current_iteration}'}},
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "emp_email",
            "foreignField": "emp_email",
            "pipeline": [
                {"$match": {"emp_status": 1}},
                {"$project": {"_id": 0, "emp_email": 1, "emp_name": 1, "emp_pref_name": 1,
                              "job_level": 1, "pml_email": 1}},
            ],
            "as": "employee",
        }
    },
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "employee.pml_email",
            "foreignField": "emp_email",
            "pipeline": [{"$project": {"_id": 0, "emp_email": 1}}],
            "as": "pml",
        },
    },
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "employee.emp_email",
            "foreignField": "pml_email",
            "pipeline": [{"$project": {"_id": 0, "emp_email": 1}}, {"$sort": {"emp_email": 1}}],
            "as": "counsellee",
        },
    },
    {
        "$lookup": {
            "from": MEETING_COLLECTION,
            "localField": "employee.emp_email",
            "foreignField": "junior",
            "pipeline": [
                {"$sort": {"iteration_number": -1}},
                {"$limit": CONNECTION_RESET},
                {"$project": {"_id": 0, "senior": 1, "iteration_number": 1}}
            ],
            "as": "junior_in_meeting",
        }
    },
    {
        "$lookup": {
            "from": MEETING_COLLECTION,
            "localField": "employee.emp_email",
            "foreignField": "senior",
            "pipeline": [
                {"$sort": {"iteration_number": -1}},
                {"$limit": CONNECTION_RESET},
                {"$project": {"_id": 0, "junior": 1, "iteration_number": 1}}
            ],
            "as": "senior_in_meeting",
        }
    },
    {
        "$project": {
            "_id": 0, "employee": 1, "pml": 1, "junior_in_meeting": 1,
            "senior_in_meeting": 1, "counsellee": 1,
            "is_senior_count": {"$size": "$senior_in_meeting"},
            "is_junior_count": {"$size": "$junior_in_meeting"},
        }
    },
    {"$sort": {"is_senior_count": 1, "is_junior_count": 1}},
]

PAIRED = [
    {"$match": {'iteration_name': '{current_iteration}'}},
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "junior",
            "foreignField": "emp_email",
            "pipeline": [{"$project": {"_id": 0, "emp_email": 1, "emp_name": 1, "emp_pref_name": 1,
                                       "job_level": 1, "pml_email": 1}}],
            "as": "junior_in_meeting",
        }
    },
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "senior",
            "foreignField": "emp_email",
            "pipeline": [{"$project": {"_id": 0, "emp_email": 1, "emp_name": 1, "emp_pref_name": 1,
                                       "job_level": 1, "pml_email": 1}}],
            "as": "senior_in_meeting",
        }
    },
    {
        "$match": {
            "$and": [
                {"junior_in_meeting": {"$size": 1}},
                {"senior_in_meeting": {"$size": 1}},
           ]
        }
    },
    {
        "$project": {
            "_id": 0, "iteration_number": 1,  "junior_in_meeting": 1,  "senior_in_meeting": 1,
        }
    }
]

UNPAIRED = [
    {"$match": {'iteration_name': '{current_iteration}'}},
    {
        "$lookup": {
            "from": ROSTER_COLLECTION,
            "localField": "emp_email",
            "foreignField": "emp_email",
            "pipeline": [
                {"$match": {"empl_class_descr": "Active Employee"}},
                {"$project": {"_id": 0, "emp_email": 1, "emp_name": 1, "emp_pref_name": 1,
                              "job_level": 1, "pml_email": 1}},
            ],
            "as": "employee",
        }
    },
    {
        "$lookup": {
            "from": MEETING_COLLECTION,
            "localField": "employee.emp_email",
            "foreignField": "junior",
            "pipeline": [
                {"$match": {'iteration_name': '{current_iteration}'}},
                {"$project": {"_id": 0, "senior": 1}}
            ],
            "as": "junior_in_meeting",
        }
    },
    {
        "$lookup": {
            "from": MEETING_COLLECTION,
            "localField": "employee.emp_email",
            "foreignField": "senior",
            "pipeline": [
                {"$match": {'iteration_name': '{current_iteration}'}},
                {"$project": {"_id": 0, "junior": 1}}
            ],
            "as": "senior_in_meeting",
        }
    },
    {
        "$match": {
            "$and": [
                {"junior_in_meeting": {"$size": 0}},
                {"senior_in_meeting": {"$size": 0}},
                {"employee": {"$size": 1}}
           ]
        }
    },
    {
        "$project": {
            "_id": 0, "iteration_number": 1, "employee": 1, "junior_in_meeting": 1,
            "senior_in_meeting": 1,
        }
    }
]
