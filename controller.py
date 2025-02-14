from mt_api.general_class import TableManger
from mt_api.base_logger import getlogger
from typing import Dict
import json
from mie_trak import MieTrak
from pprint import pprint


DEPARTMENT_DATA_FILE = r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json"


class Controller:
    def __init__(self) -> None:
        self.LOGGER = getlogger()
        self.mie_trak = MieTrak()

    def get_department_information_from_cache(self) -> Dict:
        try:
            with open(DEPARTMENT_DATA_FILE, "r") as jsonfile:
                self.cache_dict = json.load(jsonfile)
                return self.cache_dict
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

    @staticmethod
    def get_all_dashboards():
        dashboard_table = TableManger("Dashboard")
        dashboard_dict = {}
        dashboard = dashboard_table.get("DashboardPK", "Description")
        if dashboard:
            for x in dashboard:
                if x[1]:
                    dashboard_dict[x[0]] = x[1]
        return dashboard_dict

    # NOTE: this is long, might be able to make it async. 
    def add_dashboard_to_department(self, departmentpk: int, dashboardpk: int):
        user_table = TableManger("[User]")
        department_users = user_table.get("UserPK", DepartmentFK=departmentpk)

        for userpk in department_users:  # adding dashboard to all users in the department
            self.mie_trak.add_dashboard_user(dashboardpk, userpk[0])

        dashboard_table = TableManger("Dashboard")
        dashboard_description = dashboard_table.get("Description", DashboardPK=dashboardpk)

        # add new dashboard to the value in cache
        self.cache_dict[departmentpk]["accessed_dashboards"][dashboardpk] = dashboard_description[0][0] 

        self.write_cache()


