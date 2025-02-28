import win32com.client
import pythoncom
import pywintypes
from typing import Dict
import json
from scripts import mie_trak_funcs
from base_logger import getlogger


DEPARTMENT_DATA_FILE = (
    r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json"
)
LOGGER = getlogger("Controller")


class Controller:
    """
    Manages department-related data, including caching and dashboard/QuickView assignments.

    This class provides functionality to read and write cached department information,
    assign and remove dashboards and QuickViews for all users in a department, and
    update the cache accordingly.
    """

    def __init__(self) -> None:
        """
        Initializes the Controller and loads department information from the cache.
        """
        self.cache_dict = self.get_department_information_from_cache()

    def get_department_information_from_cache(self) -> Dict:
        """
        Loads department information from a cached JSON file.

        :return: A dictionary containing department information.
        :raises ValueError: If the cache file cannot be read.
        """
        try:
            with open(DEPARTMENT_DATA_FILE, "r") as jsonfile:
                return json.load(jsonfile)
        except Exception as e:
            LOGGER.critical(e)
            raise ValueError

    def write_cache(self) -> None:
        """
        Writes the current cache data to a JSON file.

        :raises ValueError: If the cache file cannot be written.
        """
        try:
            with open(DEPARTMENT_DATA_FILE, "w") as jsonfile:
                json.dump(self.cache_dict, jsonfile, indent=4)
                LOGGER.info("Cache Updated")
        except Exception as e:
            LOGGER.critical(e)
            raise ValueError

    def add_dashboard_to_department(self, departmentpk: int, dashboardpk: int):
        """
        Adds a dashboard to all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param dashboardpk: Primary key of the dashboard.
        :type dashboardpk: int
        """
        department_users = mie_trak_funcs.get_users_in_department(departmentpk).keys()

        for userpk in department_users:
            mie_trak_funcs.add_dashboard_to_user(str(dashboardpk), userpk)

        dashboard_description = mie_trak_funcs.get_entry_from_table(
            "Dashboard", dashboardpk
        ).get("Description")

        if dashboard_description:
            self.cache_dict[str(departmentpk)]["accessed_dashboards"].setdefault(
                dashboardpk, dashboard_description
            )
            LOGGER.info(
                f"Added Dashboard: {dashboardpk} to Department: {departmentpk}."
            )
            self.write_cache()

    def delete_dashboard_from_department(self, departmentpk: int, dashboardpk: int):
        """
        Removes a dashboard from all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param dashboardpk: Primary key of the dashboard.
        :type dashboardpk: int
        """
        department_users = mie_trak_funcs.get_users_in_department(departmentpk).keys()

        for userpk in department_users:
            mie_trak_funcs.delete_dashboard_from_user(userpk, dashboardpk)

        self.cache_dict[str(departmentpk)]["accessed_dashboards"].pop(
            str(dashboardpk), None
        )
        LOGGER.info(
            f"Deleted Dashboard: {dashboardpk} from department: {departmentpk}."
        )
        self.write_cache()

    def add_quickview_to_department(self, departmentpk: int, quickviewpk: int):
        """
        Adds a QuickView to all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param quickviewpk: Primary key of the QuickView.
        :type quickviewpk: int
        """
        department_users = mie_trak_funcs.get_users_in_department(departmentpk).keys()

        for userpk in department_users:
            mie_trak_funcs.add_quickview_to_user(str(quickviewpk), userpk)

        quickview_name = mie_trak_funcs.get_entry_from_table(
            "QuickView", quickviewpk
        ).get("Description")

        if quickview_name:
            self.cache_dict[str(departmentpk)].setdefault("accessed_quickviews", {})

            self.cache_dict[str(departmentpk)]["accessed_quickviews"].setdefault(
                quickviewpk, quickview_name
            )
            LOGGER.info(
                f"Added Quickview: {quickviewpk} to Department: {departmentpk}."
            )
            self.write_cache()

    def delete_quickview_from_department(
        self, cursor, departmentpk: int, quickviewpk: int
    ) -> None:
        """
        Removes a QuickView from all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param quickviewpk: Primary key of the QuickView.
        :type quickviewpk: int
        """
        department_users = mie_trak_funcs.get_users_in_department(departmentpk).keys()

        for userpk in department_users:
            mie_trak_funcs.delete_quickview_from_user(cursor, userpk, quickviewpk)

        self.cache_dict[str(departmentpk)]["accessed_quickviews"].pop(
            str(quickviewpk), None
        )
        LOGGER.info(
            f"Deleted QuickView: {quickviewpk} from department: {departmentpk}."
        )
        self.write_cache()


def send_email(to: str, subject: str, body: str):
    try:
        pythoncom.CoInitialize()  # understand why.

        try:
            outlook = win32com.client.GetActiveObject("Outlook.Application")
            LOGGER.info("Outlook application running...")
        except pywintypes.com_error:
            outlook = win32com.client.Dispatch("Outlook.Application")

        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.To = to
        mail.Body = body

        try:
            mail.Send()
            LOGGER.info(f"Email Sent to - {to}")
        except pywintypes.com_error as e:
            LOGGER.critical(f"Failed to send email: {e}")

    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")
