from mt_api.general_class import TableManger
from typing import List, Tuple, Dict
import pprint
import json


cache = {}


def build_dashboard_access():
    department_table = TableManger("Department")
    department_results = department_table.get("DepartmentPK", "Name")

    dashboard_open_access = get_dashboards_1_to_10()

    user_table = TableManger("[User]")
    for departmentpk, name in department_results:
        user_results = user_table.get("UserPK", "FirstName", "LastName", DepartmentFK=departmentpk, Enabled=1)
        if user_results:
            user_data = {userpk: [firstname, lastname] for userpk, firstname, lastname in user_results if user_results}
        else:
            user_data = None
        cache[departmentpk] = {"name": name,
                               "accessed_dashboards": dashboard_open_access,
                               "users": user_data,}
    write_cache()


def get_dashboards_1_to_10() -> Dict[int, str]:
    dashboard_table = TableManger("Dashboard")
    results: List[Tuple[int, str]] = dashboard_table.get("DashboardPK", "Description")

    if not results:
        raise ValueError("Mie Trak did not return anything")

    return {pk: description for pk, description in results if description and description[0].isnumeric()}


def write_cache():
    with open(r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json", "w") as jsonfile:
        json.dump(cache, jsonfile)

    # TESTING:
    with open(r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json", "r") as jsonfile:
        pprint.pprint(json.load(jsonfile))
