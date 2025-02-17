from mt_api.general_class import TableManger
from typing import Dict, List, Tuple
from mt_api.connection import get_connection


def get_all_quickviews():
    quick_view_table = TableManger("QuickView")

    quick_view_dict = {}
    quick_view = quick_view_table.get("QuickViewPK", "Description")

    if quick_view:
        for x in quick_view:
            quick_view_dict[str(x[0])] = x[1]

    return quick_view_dict


def add_quickview_to_user(quickview_pk, user_fk):
    quickview_users_table = TableManger("QuickViewUser")

    pk = quickview_users_table.get("QuickViewUserPK", UserFK=user_fk, QuickViewFK=quickview_pk)
    if not pk:
        info_dict = {
            "QuickViewFK": quickview_pk,
            "UserFK": user_fk
        }
        pk = quickview_users_table.insert(info_dict)
    return pk


def get_all_dashboards() -> Dict[str, str]:
    """
    Returns all dashboards from Mie Trak Dashboard Table.
    """

    dashboard_table = TableManger("Dashboard")
    dashboard_dict = {}

    dashboard = dashboard_table.get("DashboardPK", "Description")
    if dashboard:
        for x in dashboard:
            if x[1]:
                dashboard_dict[str(x[0])] = x[1]

    return dashboard_dict


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
        WHERE qu.UserFK = %s;
            """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (userpk,))

        results = cursor.fetchall()

        return {str(quickview_pk): description for quickview_pk, description in results}


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

        return {str(dashboard_pk): description for dashboard_pk, description in results}


def add_dashboard_to_user(dashboard_pk: str, user_fk: int):
    """
    [TODO:description]

    :param dashboard_pk: [TODO:description]
    :param user_fk: [TODO:description]
    """

    dashboard_user_table = TableManger("DashboardUser")

    pk = dashboard_user_table.get("DashboardUserPK", DashboardFK=dashboard_pk, UserFK = user_fk)
    if not pk:
        info_dict = {
            "DashboardFK": dashboard_pk,
            "UserFK": user_fk
        }
        pk = dashboard_user_table.insert(info_dict)

    return pk


def get_user_data(enabled=False, not_active=False, departmentfk=None) -> Dict[int, List[str]]:
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


