import sys
from utils.constants import SUBJECT_DATA


def get_class_and_test_id(subject):
  if subject in SUBJECT_DATA:
    classId, testId = SUBJECT_DATA[subject]
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