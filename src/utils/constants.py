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
    "moh":(286797,113417),
    "amcmock": (292554, 119729),
}
SUBJECT = {
    
}
LMS_API_HEADERS = {"apiKey": "8209d837743ef9f4b1699ffaa36fe69a", "ORGID": "5735"}

WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf"