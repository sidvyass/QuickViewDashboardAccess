from mt_api.general_class import TableManger
from typing import Dict, List, Tuple


def get_all_quickviews():
    quick_view_table = TableManger("QuickView")

    quick_view_dict = {}
    quick_view = quick_view_table.get("QuickViewPK", "Description")

    if quick_view:
        for x in quick_view:
            quick_view_dict[str(x[0])] = x[1]

    return quick_view_dict


def add_user_quickview(quickview_pk, user_fk):
    quickview_users_table = TableManger("QuickViewUser")

    pk = quickview_users_table.get("QuickViewUserPK", UserFK=user_fk, QuickViewFK=quickview_pk)
    if not pk:
        info_dict = {
            "QuickViewFK": quickview_pk,
            "UserFK": user_fk
        }
        pk = quickview_users_table.insert(info_dict)
    return pk


def get_all_dashboards():
    dashboard_table = TableManger("Dashboard")
    dashboard_dict = {}
    dashboard = dashboard_table.get("DashboardPK", "Description")
    if dashboard:
        for x in dashboard:
            if x[1]:
                dashboard_dict[str(x[0])] = x[1]
    return dashboard_dict


def get_user_quick_view(userpk):
    quick_view_table = TableManger("QuickView")

    quick_view_users_table = TableManger("QuickViewUser")
    user_quick_view = quick_view_users_table.get("QuickViewFK", UserFK=userpk)

    quick_view = {}
    if user_quick_view:
        for quick_view_fk in user_quick_view:
            quick_view_name = quick_view_table.get("Description", QuickViewPK=quick_view_fk[0])
            if quick_view_name:
                quick_view[quick_view_fk[0]] = quick_view_name[0][0]

    return quick_view


def get_user_dashboards(userpk):
    dashboard_table = TableManger("Dashboard")

    dashboard_user_table = TableManger("DashboardUser")
    user_accessed_dashboard = dashboard_user_table.get("DashboardFK", UserFK= userpk)

    dashboards = {}
    if user_accessed_dashboard:
        for dashboard_pk in user_accessed_dashboard:
            dashboard_name = dashboard_table.get("Description", DashboardPK= dashboard_pk[0])
            if dashboard_name:  # Check if a result is returned
                dashboards[dashboard_pk[0]] = dashboard_name[0][0]

    return dashboards


def add_dashboard_user(dashboard_pk, user_fk):
    dashboard_user_table = TableManger("DashboardUser")

    pk = dashboard_user_table.get("DashboardUserPK", DashboardFK=dashboard_pk, UserFK = user_fk)
    if not pk:
        info_dict = {
            "DashboardFK": dashboard_pk,
            "UserFK": user_fk
        }
        pk= dashboard_user_table.insert(info_dict)
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


