import random

SUBJECT_DATA = {
    "medicos": (262859, 89822),
    "adc": (272073, 98161),
    "nclex": (280097, 105398),
    "usmle": (262232, 91181),
    "apc": (271165, 97775),
    "ocanz": (285909, 113240),
    "psi": (286125, 113417),
    "sple": (286126, 113418),
    "moh":(286797,113417),
    "kaps": {
        "class_id": 238659,
        "test_id": 74556,
        "topics": [
            {
                "name": "CVS",
                "total_questions": "5",
            },
            {
                "name": "ANS",
                "total_questions": "5",
            },
            {
                "name": "Biopharmaceutics And Calculations",
                "total_questions": "5",
            },
            {
                "name": "GIT",
                "total_questions": "5",
            },
            {
                "name": "CNS",
                "total_questions": "5",
            },
            {
                "name": "Drug Interaction",
                "total_questions": "5",
            },
            {
                "name": "Pharmaceutics",
                "total_questions": "5",
            },
            {
                "name": "Antimicrobials, Anti-Cancer, Toxicology",
                "total_questions": "5",
            },
            {
                "name": "Endocrinology",
                "total_questions": "5",
            },
            {
                "name": "Chemistry",
                "total_questions": "5",
            }
        ],
        "total_questions": 50,
        "total_marks": 50,
        "max_time": 60, # in minutes
    },
    "amcmock": {
        "class_id": 292554,
        "test_id": 119729,
        "topics": [
            {
                "name": "CVS",
                "total_questions": "15"
            },
            {
                "name": "Mental Health",
                "total_questions": "15"
            },
            {
                "name": "Women Health",
                "total_questions": "15"
            },
            {
                "name": "Respiratory",
                "total_questions": "15"
            },
            {
                "name": "Hematology",
                "total_questions": "15"
            },
            {
                "name": "Dermatology",
                "total_questions": "15"
            },
            {
                "name": "Urology",
                "total_questions": "15"
            },
            {
                "name": "Infectious Disease",
                "total_questions": "15"
            },
            {
                "name": "Breast and Endocrine System",
                "total_questions": "15"
            },
            {
                "name": "ENT and Ophthalmology",
                "total_questions": "15"
            }
        ],
        "total_questions": 150,
        "total_marks": 150,
        "max_time": 210, # in minutes
    }
}

LMS_API_HEADERS = {"apiKey": "8209d837743ef9f4b1699ffaa36fe69a", "ORGID": "5735"}

# WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf" # FOR MAC - "/usr/local/bin/wkhtmltopdf"    # FOR WINDOWS - "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
CUSTOM_TOP_10_STUDENTS_TIME_TAKEN = [random.randint(40, 50) for _ in list(range(1, 11))]
