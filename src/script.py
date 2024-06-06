import sys

subject_data = {
  'kaps': (238659, 74556),
  'medicos': (262859, 89822),
  'adc': (272073, 98161),
  'nclex': (280097, 105398),
  'usmle': (262232, 91181),
  'apc': (271165, 97775),
  'ocanz': (285909, 113240),
  'psi': (286125, 113417),
  'sple': (286126, 113418),
}

def get_class_and_test_id(subject):
  if subject in subject_data:
    classId, testId = subject_data[subject]
    return classId, testId
  else:
    return None  

if len(sys.argv) > 2:
    e = sys.argv[1]
    f = sys.argv[2]
    print(f"Student ID: {e}")
    print(f"Student ID: {f}")
    
    subject = 'medicos'
    classId, testId = get_class_and_test_id(subject)

    if classId and testId:
        print(f"Class ID: {classId}, Test ID: {testId}")
    else:
        print("Invalid subject selected")

else:
    print("No student ID provided.")