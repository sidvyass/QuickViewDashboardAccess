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

    # NOTE: Disapprove does not do anything inside Mie Trak.
    # So we just update our cache to never accept duplicate keys.
    def append_requests(self, value: Dict, approved=False):
        l = self.approved_requests if approved else self.disapproved_requests

        keys = [val.get("Vacation ID", "") for val in l]
        id = value.get("Vacation ID", "")  # id to add
