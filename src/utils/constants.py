import random

LMS_API_HEADERS = {"apiKey": "62fd09ca0e4bda109687a49faee18bcd", "ORGID": "5735"}

WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf" # FOR MAC - "/usr/local/bin/wkhtmltopdf"    # FOR WINDOWS - "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"

CUSTOM_TOP_10_STUDENTS_TIME_TAKEN = [random.randint(40, 50) for _ in list(range(1, 11))]

QUALIFICATION_DATA = {
    "pharmacy": {
        "scholarships": {
            "kaps": {
                "class_id": 238659,
                "test_id": 74556,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            },
            "sple": {
                "class_id": 286126,
                "test_id": 113418,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            },
            "psi": {
                "class_id": 286125,
                "test_id": 113417,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            },
            "moh": {
                "class_id": 286797,
                "test_id": 113417,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            }
        },
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
    },
    "dentistry": {
        "scholarships": {
            "adc": {
                "class_id": 272073,
                "test_id": 98161,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            }
        },
        "topics": [
            {
                "name": "Carries",
                "total_questions": "5"
            },
            {
                "name": "Periodontics",
                "total_questions": "5"
            },
            {
                "name": "Endodontics",
                "total_questions": "5"
            },
            {
                "name": "Oral Pathology",
                "total_questions": "5"
            },
            {
                "name": "Operative",
                "total_questions": "5"
            },
            {
                "name": "Oral Radiology",
                "total_questions": "5"
            },
            {
                "name": "Oral Surgery",
                "total_questions": "5"
            },
            {
                "name": "Ortho",
                "total_questions": "5"
            },
            {
                "name": "Dental Material",
                "total_questions": "5"
            },
            {
                "name": "Dental Implant",
                "total_questions": "5"
            }
        ],
        "total_questions": 50,
        "total_marks": 50,
        "max_time": 60
    },
    "nursing": {
        "scholarships": {
            "nclex": {
                "class_id": 280097,
                "test_id": 105398,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            }
        },
        "topics": [
            {
                "name": "GI System II",
                "total_questions": "5"
            },
            {
                "name": "Neurology",
                "total_questions": "5"
            },
            {
                "name": "Urinary System I",
                "total_questions": "5"
            },
            {
                "name": "Endocrine System",
                "total_questions": "5"
            },
            {
                "name": "ENT",
                "total_questions": "5"
            },
            {
                "name": "Pediatric Nursing",
                "total_questions": "5"
            },
            {
                "name": "Musculoskeletal System",
                "total_questions": "5"
            },
            {
                "name": "OBG",
                "total_questions": "5"
            },
            {
                "name": "Psychiatric",
                "total_questions": "5"
            },
            {
                "name": "Emergency",
                "total_questions": "5"
            }
        ],
        "total_questions": 50,
        "total_marks": 50,
        "max_time": 60
    },
    "physiotherapy": {
        "scholarships": {
            "apc": {
                "class_id": 271165,
                "test_id": 97775,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            }
        },
        "topics": [
            {
                "name": "Asthma",
                "total_questions": "5"
            },
            {
                "name": "PT Management",
                "total_questions": "5"
            },
            {
                "name": "MSK",
                "total_questions": "5"
            },
            {
                "name": "ICD",
                "total_questions": "5"
            },
            {
                "name": "GBS",
                "total_questions": "5"
            },
            {
                "name": "Cardiopulmonary",
                "total_questions": "5"
            },
            {
                "name": "Cardiac Rehabilitation",
                "total_questions": "5"
            },
            {
                "name": "ECG",
                "total_questions": "5"
            },
            {
                "name": "Stroke",
                "total_questions": "5"
            },
            {
                "name": "MUSC",
                "total_questions": "5"
            }
        ],
        "total_questions": 50,
        "total_marks": 50,
        "max_time": 60
    },
    "optometry": {
        "scholarships": {
            "ocanz": {
                "class_id": 285909,
                "test_id": 113240,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            }
        },
        "topics": [
            {
                "name": "EYE EXAMINATION & DIAGNOSTICS",
                "total_questions": "5"
            },
            {
                "name": "SPECTACLE",
                "total_questions": "5"
            },
            {
                "name": "CONTACT LENS",
                "total_questions": "5"
            },
            {
                "name": "LOW VISION & BV",
                "total_questions": "5"
            },
            {
                "name": "LIDS AND LACRIMAL SYSTEM",
                "total_questions": "5"
            },
            {
                "name": "CONJUNCTIVA, CORNEA, LENS",
                "total_questions": "5"
            },
            {
                "name": "UVEA",
                "total_questions": "5"
            },
            {
                "name": "ECG",
                "total_questions": "5"
            },
            {
                "name": "GLAUCOMA",
                "total_questions": "5"
            },
            {
                "name": "RETINA",
                "total_questions": "5"
            }
        ],
        "total_questions": 50,
        "total_marks": 50,
        "max_time": 60
    },
    "medicine": {
        "scholarships": {
            "usmle": {
                "class_id": 262232,
                "test_id": 91181,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60,
                "topics": [
                    {
                        "name": "Embryology",
                        "total_questions": "5"
                    },
                    {
                        "name": "Microbiology",
                        "total_questions": "5"
                    },
                    {
                        "name": "Biochemistry",
                        "total_questions": "5"
                    },
                    {
                        "name": "Biostatistics",
                        "total_questions": "5"
                    },
                    {
                        "name": "Pathology",
                        "total_questions": "5"
                    },
                    {
                        "name": "Anatomy",
                        "total_questions": "5"
                    },
                    {
                        "name": "Histology",
                        "total_questions": "5"
                    },
                    {
                        "name": "Genetics",
                        "total_questions": "5"
                    },
                    {
                        "name": "Immunology",
                        "total_questions": "5"
                    },
                    {
                        "name": "Pharmacology",
                        "total_questions": "5"
                    }
                ],
            },
            "medicos": {
                "class_id": 262859,
                "test_id": 89822,
                "total_questions": 50,
                "total_marks": 50,
                "max_time": 60
            },
            "amcmock": {
                "class_id": 292554,
                "test_id": 119729,
                "total_questions": 150,
                "total_marks": 150,
                "max_time": 210
            }
        },
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
    },
}
