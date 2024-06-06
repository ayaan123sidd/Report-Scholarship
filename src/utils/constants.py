'''
    SUBJECT DATA FORMAT

    KEY: The name of the subject
    VALUE: Tuple containing the class_id and the test_id
'''
SUBJECT_DATA = {
    "kaps": (238659, 74556),
    "medicos": (262859, 89822),
    "adc": (272073, 98161),
    "nclex": (280097, 105398),
    "usmle": (262232, 91181),
    "apc": (271165, 97775),
    "ocanz": (285909, 113240),
    "psi": (286125, 113417),
    "sple": (286126, 113418),
}

LMS_API_HEADERS = {"apiKey": "e63cb1851964c2aea0c3a1836cdd4b98", "ORGID": "5735"}

WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf"