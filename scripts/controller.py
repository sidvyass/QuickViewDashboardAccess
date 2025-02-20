from mt_api.general_class import TableManger
from mt_api.base_logger import getlogger
from typing import Dict
import json
from pprint import pprint
from scripts import mie_trak_funcs


DEPARTMENT_DATA_FILE = (
    r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json"
)


class Controller:
    def __init__(self) -> None:
        self.LOGGER = getlogger()
        self.cache_dict = self.get_department_information_from_cache()

    def get_department_information_from_cache(self) -> Dict:
        try:
            with open(DEPARTMENT_DATA_FILE, "r") as jsonfile:
                return json.load(jsonfile)
        except Exception as e:
            self.LOGGER.error(e)
            raise ValueError

    def write_cache(self) -> None:
        try:
            with open(DEPARTMENT_DATA_FILE, "w") as jsonfile:
                json.dump(self.cache_dict, jsonfile)
        except Exception as e:
            self.LOGGER.error(e)
            raise ValueError

    # NOTE: this is long, might be able to make it async.
    def add_dashboard_to_department(self, departmentpk: int, dashboardpk: int):
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for (
            userpk
        ) in department_users:  # adding dashboard to all users in the department
            mie_trak_funcs.add_dashboard_to_user(str(dashboardpk), userpk[0])

        dashboard_table = TableManger("Dashboard")
        dashboard_description = dashboard_table.get(
            "Description", DashboardPK=dashboardpk
        )

        # add new dashboard to the value in cache
        self.cache_dict[departmentpk]["accessed_dashboards"][dashboardpk] = (
            dashboard_description[0][0]
        )

        self.write_cache()

    def delete_dashboard_from_department(self, departmentpk: int, dashboardpk: int):
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for (
            userpk
        ) in department_users:  # adding dashboard to all users in the department
            mie_trak_funcs.delete_dashboard_from_user(userpk[0], dashboardpk)

        del self.cache_dict[departmentpk]["accessed_dashboards"][dashboardpk]

        self.write_cache()

    def add_quickview_to_department(self, departmentpk: int, quickviewpk: int):
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for (
            userpk
        ) in department_users:  # adding dashboard to all users in the department
            mie_trak_funcs.add_quickview_to_user(quickviewpk, userpk[0])

        quickview_table = TableManger("QuickView")
        quickview_name = quickview_table.get("Description", QuickViewPK=quickviewpk)

        self.cache_dict[departmentpk]["accessed_quickviews"][quickviewpk] = (
            quickview_name
        )

        self.write_cache()

    def delete_quickview_from_user(self, departmentpk, quickviewpk: int) -> None:
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for userpk in department_users:
            mie_trak_funcs.delete_quickview_from_user(userpk, quickviewpk)

        del self.cache_dict[departmentpk]["accessed_quickviews"][quickviewpk]

        self.write_cache()


# NOTE: This is a script that was run initally to build a config file.
# The config file is found in the data folder.

cache = {}


def build_dashboard_access():
    department_table = TableManger("Department")
    department_results = department_table.get("DepartmentPK", "Name")

    dashboard_open_access = get_dashboards_1_to_10()

    user_table = TableManger("[User]")
    for departmentpk, name in department_results:
        user_results = user_table.get(
            "UserPK", "FirstName", "LastName", DepartmentFK=departmentpk, Enabled=1
        )
        if user_results:
            user_data = {
                userpk: [firstname, lastname]
                for userpk, firstname, lastname in user_results
                if user_results
            }
        else:
            user_data = None
        cache[departmentpk] = {
            "name": name,
            "accessed_dashboards": dashboard_open_access,
            "users": user_data,
        }
    write_cache()


def get_dashboards_1_to_10() -> Dict[int, str]:
    dashboard_table = TableManger("Dashboard")
    results: List[Tuple[int, str]] = dashboard_table.get("DashboardPK", "Description")

    if not results:
        raise ValueError("Mie Trak did not return anything")

    return {
        pk: description
        for pk, description in results
        if description and description[0].isnumeric()
    }


def write_cache():
    with open(
        r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json", "w"
    ) as jsonfile:
        json.dump(cache, jsonfile)

    # TESTING:
    with open(
        r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json", "r"
    ) as jsonfile:
        pprint(json.load(jsonfile))
