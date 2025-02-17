from mt_api.general_class import TableManger
from mt_api.base_logger import getlogger
from typing import Dict
import json
from pprint import pprint
from scripts import mie_trak_funcs


DEPARTMENT_DATA_FILE = r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json"


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

        for userpk in department_users:  # adding dashboard to all users in the department
            mie_trak_funcs.add_dashboard_user(dashboardpk, userpk[0])

        dashboard_table = TableManger("Dashboard")
        dashboard_description = dashboard_table.get("Description", DashboardPK=dashboardpk)

        # add new dashboard to the value in cache
        self.cache_dict[departmentpk]["accessed_dashboards"][dashboardpk] = dashboard_description[0][0] 

        self.write_cache()

    def delete_dashboard_from_department(self, departmentpk: int, dashboardpk: int):
        pass

    def add_quickview_to_department(self, departmentpk: int, quickviewpk: int):
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for userpk in department_users:  # adding dashboard to all users in the department
            mie_trak_funcs.add_user_quickview(quickviewpk, userpk[0])

        quickview_table = TableManger("QuickView")
        quickview_name = quickview_table.get("Description", QuickViewPK=quickviewpk)

        self.cache_dict[departmentpk]["accessed_quickviews"][quickviewpk] = quickview_name

        self.write_cache()

    def add_user_to_dashboard_or_quickview(self, userpk: int, dashboard_quickview_pk: int, type: str = "Dashboard"):
        pass
