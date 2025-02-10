from pprint import pprint
from mt_api.general_class import TableManger
from typing import List, Tuple, Dict


# List these to one side
def get_all_dashboards() -> List[Tuple[int, str]]:
    dashboard_table = TableManger("Dashboard")
    dashboards = dashboard_table.get("DashboardPK", "Description")
    return dashboards

# List these to one side
def get_active_users() -> Dict[int, List[str]]:
    dashboard_user_table = TableManger("DashboardUser")
    dashboard_table = TableManger("Dashboard")

    user_table = TableManger("[user]")
    results = user_table.get("UserPK", "FirstName", "LastName", enabled=True)

    user_dashboard_dict = {}

    for userpk, firstname, lastname in results:
        accessed_dashboards = dashboard_user_table.get("DashboardFK", userFK=userpk)
        accessed_dashboard_names = []
        if accessed_dashboards:
            for dashboardfk in accessed_dashboards:
                description = dashboard_table.get("dashboardpk", "Description", dashboardpk=dashboardfk[0])
                accessed_dashboard_names.append(description)

        user_dashboard_dict[userpk] = {
                        "accessed_dashboards": accessed_dashboard_names,
                        "firstname": firstname,
                        "lastname": lastname,
                                       }

    return user_dashboard_dict


def assign_user_access_to_dashboards(userpk: int, dashboards: List[Tuple[int, str]]) -> None:
    dashboard_user_table = TableManger("DashboardUser")
    for dashboardpk, description in dashboards:
        update_dict = {"DashboardFK": str(dashboardpk),
                       "UserFK": str(userpk),}
        dashboard_user_table.insert(update_dict)


