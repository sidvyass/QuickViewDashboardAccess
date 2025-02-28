import win32com.client
import pythoncom
import pywintypes
import functools
import pyodbc
from contextlib import closing
from typing import Dict, Callable
import json
from scripts import mie_trak_funcs
from scripts.mie_trak_funcs import DSN
from base_logger import getlogger


DEPARTMENT_DATA_FILE = (
    r"C:\PythonProjects\QuickViewDashboardAccess\data\department_data.json"
)
LOGGER = getlogger("Controller")


class Controller:
    def __init__(self) -> None:
        self.cache_dict = self.get_department_information_from_cache()

    @staticmethod
    def with_db_conn(commit: bool = False):
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    with pyodbc.connect(DSN) as conn:
                        with closing(conn.cursor()) as cursor:
                            result = func(self, cursor, *args, **kwargs)
                            if commit:
                                conn.commit()
                            return result
                except pyodbc.OperationalError as vpn_err:
                    LOGGER.error(f"VPN not connected. Could not connect.\n{vpn_err}")
                    raise
                except pyodbc.Error as db_err:
                    LOGGER.error(f"Database Error in {func.__name__}: {db_err}")
                    raise
                except Exception as e:
                    LOGGER.error(f"Unexpected Error in {func.__name__}: {e}")
                    raise

            return wrapper

        return decorator

    def get_department_information_from_cache(self) -> Dict:
        try:
            with open(DEPARTMENT_DATA_FILE, "r") as jsonfile:
                return json.load(jsonfile)
        except Exception as e:
            LOGGER.error(e)
            raise ValueError

    def write_cache(self) -> None:
        try:
            with open(DEPARTMENT_DATA_FILE, "w") as jsonfile:
                json.dump(self.cache_dict, jsonfile)
                LOGGER.info("Cache Updated")
        except Exception as e:
            LOGGER.error(e)
            raise ValueError

    @with_db_conn()
    def add_dashboard_to_department(self, cursor, departmentpk: int, dashboardpk: int):
        """
        Adds a dashboard to all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param dashboardpk: Primary key of the dashboard.
        :type dashboardpk: int
        """
        query_users = "SELECT UserPK FROM [User] WHERE DepartmentFK = ?"
        cursor.execute(query_users, (departmentpk,))
        department_users = cursor.fetchall()

        for userpk in department_users:
            mie_trak_funcs.add_dashboard_to_user(str(dashboardpk), userpk[0])
            # LOGGER.debug(f"Added DashboardPK: {dashboardpk} To UserPK: {userpk}")

        query_dashboard = "SELECT Description FROM Dashboard WHERE DashboardPK = ?"
        cursor.execute(query_dashboard, (dashboardpk,))
        dashboard_description = cursor.fetchone()

        if dashboard_description:
            self.cache_dict[str(departmentpk)]["accessed_dashboards"].setdefault(
                dashboardpk, dashboard_description[0]
            )
            LOGGER.info(
                f"Added Dashboard: {dashboardpk} to Department: {departmentpk}."
            )
            self.write_cache()

    @with_db_conn()
    def delete_dashboard_from_department(
        self, cursor, departmentpk: int, dashboardpk: int
    ):
        """
        Removes a dashboard from all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param dashboardpk: Primary key of the dashboard.
        :type dashboardpk: int
        """
        query_users = "SELECT UserPK FROM [User] WHERE DepartmentFK = ?"
        cursor.execute(query_users, (departmentpk,))
        department_users = cursor.fetchall()

        for userpk in department_users:
            mie_trak_funcs.delete_dashboard_from_user(cursor, userpk[0], dashboardpk)

        self.cache_dict[str(departmentpk)]["accessed_dashboards"].pop(
            str(dashboardpk), None
        )
        LOGGER.info(
            f"Deleted Dashboard: {dashboardpk} from department: {departmentpk}."
        )
        self.write_cache()

    @with_db_conn()
    def add_quickview_to_department(self, cursor, departmentpk: int, quickviewpk: int):
        """
        Adds a QuickView to all users in a department.

        :param cursor: Database cursor.
        :type cursor: pyodbc.Cursor
        :param departmentpk: Primary key of the department.
        :type departmentpk: int
        :param quickviewpk: Primary key of the QuickView.
        :type quickviewpk: int
        """
        query_users = "SELECT UserPK FROM [User] WHERE DepartmentFK = ?"
        cursor.execute(query_users, (departmentpk,))
        department_users = cursor.fetchall()

        for userpk in department_users:
            mie_trak_funcs.add_quickview_to_user(str(quickviewpk), userpk[0])

        query_quickview = "SELECT Description FROM QuickView WHERE QuickViewPK = ?"
        cursor.execute(query_quickview, (quickviewpk,))
        quickview_name = cursor.fetchone()

        if quickview_name:
            self.cache_dict[str(departmentpk)].setdefault("accessed_quickviews", {})

            self.cache_dict[str(departmentpk)]["accessed_quickviews"][
                str(quickviewpk)
            ] = quickview_name[0]
            LOGGER.info(
                f"Added Quickview: {quickviewpk} to Department: {departmentpk}."
            )
            self.write_cache()

    @with_db_conn()
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
        query_users = "SELECT UserPK FROM [User] WHERE DepartmentFK = ?"
        cursor.execute(query_users, (departmentpk,))
        department_users = cursor.fetchall()

        for userpk in department_users:
            mie_trak_funcs.delete_quickview_from_user(cursor, userpk[0], quickviewpk)

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
