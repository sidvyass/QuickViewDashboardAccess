from mt_api.general_class import TableManger
from typing import Dict, List, Tuple, Any
from mt_api.connection import get_connection
from datetime import datetime


def get_all_quickviews():
    query = "SELECT QuickviewPK, Description FROM QuickView"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

        return {
            str(quickview_pk): description
            for quickview_pk, description in results
            if description
        }


def get_all_dashboards() -> Dict[str, str]:
    """
    Returns all dashboards from Mie Trak Dashboard Table.
    """
    query = "SELECT DashboardPK, Description FROM Dashboard;"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

        return {
            str(dashboard_pk): description
            for dashboard_pk, description in results
            if description
        }


def get_user_quick_view(userpk) -> Dict[str, str]:
    """
    Returns all quickviews accessed by the User. Ref QuickViewUser Table in Mie Trak.

    :param userpk int: Primay Key from User Table.
    :return: quickview_pk - description dict.
    """

    query = """
        SELECT q.QuickViewPK, q.Description
        FROM QuickViewUser qu
        JOIN QuickView q ON qu.QuickViewFK = q.QuickViewPK
        WHERE qu.UserFK = ?;
            """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (userpk,))

        results = cursor.fetchall()

        return {
            str(quickview_pk): description
            for quickview_pk, description in results
            if description
        }


def get_user_dashboards(userpk: int) -> Dict[str, str]:
    """
    Gets all dashboards the user has access to and returns a dict.

    :param userpk int: primary key of the user.
    :return: DashboardPK: Dashboard Description
    """

    query = """
        SELECT d.DashboardPK, d.Description
        FROM DashboardUser du
        JOIN Dashboard d ON du.DashboardFK = d.DashboardPK
        WHERE du.UserFK = ?;
            """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (userpk,))

        results = cursor.fetchall()

        return {
            str(dashboard_pk): description
            for dashboard_pk, description in results
            if description
        }


def add_dashboard_to_user(dashboard_pk: str, user_fk: int):
    """
    [TODO:description]

    :param dashboard_pk: [TODO:description]
    :param user_fk: [TODO:description]
    """

    dashboard_user_table = TableManger("DashboardUser")

    pk = dashboard_user_table.get(
        "DashboardUserPK", DashboardFK=dashboard_pk, UserFK=user_fk
    )
    if not pk:
        info_dict = {"DashboardFK": dashboard_pk, "UserFK": user_fk}
        pk = dashboard_user_table.insert(info_dict)

    return pk


def add_quickview_to_user(quickview_pk, user_fk):
    quickview_users_table = TableManger("QuickViewUser")

    pk = quickview_users_table.get(
        "QuickViewUserPK", UserFK=user_fk, QuickViewFK=quickview_pk
    )
    if not pk:
        info_dict = {"QuickViewFK": quickview_pk, "UserFK": user_fk}
        pk = quickview_users_table.insert(info_dict)
    return pk


def get_user_data(
    enabled=False, not_active=False, departmentfk=None
) -> Dict[int, List[str]]:
    user_table = TableManger("[User]")

    user_dict = {}
    if enabled:
        user = user_table.get("UserPK", "FirstName", "LastName", Enabled=1)
    elif not_active:
        user = user_table.get("UserPK", "FirstName", "LastName", Enabled=0)
    elif departmentfk:
        user = user_table.get(
            "UserPK", "FirstName", "LastName", DepartmentFK=departmentfk, Enabled=1
        )
    else:
        user = user_table.get("UserPK", "FirstName", "LastName")

    if not user:
        raise ValueError("Mie Trak did not return any values. Check last query.")

    for x in user:
        if x:
            user_dict[x[0]] = [x[1], x[2]]
    return user_dict


def get_all_departments():
    """Returns all the Department data in the form of a dict with DepartmentPK as Key and Name as value"""
    department_table = TableManger("Department")

    department_dict = {}
    departments = department_table.get("DepartmentPK", "Name")
    if departments:
        for x in departments:
            if x[1]:
                department_dict[x[0]] = x[1]
    return department_dict


def delete_dashboard_from_user(userpk: int, dashboardpk: int) -> None:
    query = "DELETE FROM DashboardUser WHERE UserFK = ? AND DashboardFK = ?;"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (userpk, dashboardpk))


def delete_quickview_from_user(userpk: int, quickviewpk: int) -> None:
    query = "DELETE FROM QuickViewUser WHERE UserFK = ? AND QuickViewFK = ?;"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (userpk, quickviewpk))


def get_all_vacation_requests() -> List:
    query = """
            SELECT v.VacationRequestPK, u.firstname, u.lastname, v.FromDate, v.ToDate, v.StartTime, v.Hours, v.Reason, v.Approved
            FROM VacationRequest v
            JOIN [User] u ON v.EmployeeFK = u.UserPK 
            WHERE v.Approved = 0
            ORDER BY v.VacationRequestPK DESC;
            """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

    if not results:
        raise ValueError("Mie Trak did not return anything. Check Query.")

    return _format_results(results)


def _format_results(data):
    formatted_data = []
    for row in data:
        (
            vacation_id,
            first_name,
            last_name,
            from_date,
            to_date,
            start_time,
            hours,
            reason,
            approved,
        ) = row
        formatted_row = {
            "Vacation ID": vacation_id,
            "Employee": f"{first_name} {last_name}",
            "From Date": from_date.strftime("%Y-%m-%d") if from_date else "N/A",
            "To Date": to_date.strftime("%Y-%m-%d") if to_date else "N/A",
            "Start Time": datetime.strptime(start_time[:15], "%H:%M:%S.%f").strftime(
                "%I:%M %p"
            )
            if start_time
            else "N/A",
            "Hours": float(hours) if hours else "N/A",
            "Reason": reason,
            "Approved": approved,
        }
        formatted_data.append(formatted_row)
    return formatted_data


def approve_vacation_request(request_pk: int):
    query = """
        UPDATE VacationRequest
        SET Approved = 1
        WHERE VacationRequestPK = ?
            """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (request_pk,))
