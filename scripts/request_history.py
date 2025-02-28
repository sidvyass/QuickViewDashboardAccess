from typing import List, Dict, Any
import json


class RequestHistory:
    def __init__(self):
        try:
            with open(
                r"C:\PythonProjects\QuickViewDashboardAccess\data\past_requests.json",
                "r",
            ) as jsonfile:
                data = json.load(jsonfile)
                self.approved_requests = data.get("approved_requests")
                self.disapproved_requests = data.get("disapproved_requests")
        except Exception as e:
            print(e)
            self.approved_requests: List[Dict[str, Any]] = []
            self.disapproved_requests: List[Dict[str, Any]] = []

    def write_cache(self):
        data = {
            "approved_requests": self.approved_requests,
            "disapproved_requests": self.disapproved_requests,
        }

        with open(
            r"C:\PythonProjects\QuickViewDashboardAccess\data\past_requests.json", "w"
        ) as jsonfile:
            json.dump(data, jsonfile, indent=4)
