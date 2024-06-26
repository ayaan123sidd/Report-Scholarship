import requests


class ExerciseService:
    def __init__(self, headers, base_url=None):
        self.headers = headers
        self.base_url = base_url or "http://lms.academically.com/nuSource/api/v1/exercises"


    def get_attempt_data(self, test_id, class_id, student_id):
        url = f"{self.base_url}/{test_id}/attemptlist?class_id={class_id}&user_id={student_id}&is_quiz=false"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception("Failed to connect to the API while getting attempt data.")
        
        return response.json()


    def get_exercise_data(self, attempt_id):
        url = f"{self.base_url}/pasttest/{attempt_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception("Failed to connect to the API while getting exercise data.")
        
        return response.json()
            
