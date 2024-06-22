import requests


class ReportService:
    def __init__(self, headers, params=None, base_url=None):
        self.headers = headers
        self.base_url = base_url or "http://lms.academically.com/nuSource/api/v1/reports"
        self.params = params


    def get_class_progress_report(self, class_id, page=1, per_page=5000):   # PAGE & PER PAGE DATA IS HARDCODED
        url = f"{self.base_url}/classprogress"
        default_params = {"class_id": class_id, "page": page, "per_page": per_page}
        params = self.params or default_params

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch report data.")
