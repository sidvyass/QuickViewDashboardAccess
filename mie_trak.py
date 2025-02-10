from mt_api.general_class import TableManger
from tkinter import messagebox
from datetime import datetime
from typing import List, Dict


class MieTrak:
    def __init__(self):
        self.user_table = TableManger("[User]")
        self.quick_view_table = TableManger("QuickView")
        self.quick_view_users_table = TableManger("QuickViewUser")
        self.dashboard_table = TableManger("Dashboard")
        self.dashboard_user_table = TableManger("DashboardUser")

        self.vacation_request_table = TableManger("VacationRequest")
        self.department_table = TableManger("Department")

    def get_user_data(self, enabled=False, not_active=False, departmentfk=None) -> Dict[int, List[str]]:
        """Returns all the user data in the form of a dict with UserPK as Key and FirstName as Value

        Returns:
            dict = {"UserPK": "FirstName"}
        """
        user_dict = {}
        if enabled:
            user = self.user_table.get("UserPK", "FirstName", "LastName", Enabled=1)
        elif not_active:
            user = self.user_table.get("UserPK", "FirstName", "LastName", Enabled=0)
        elif departmentfk:
            user = self.user_table.get(
                "UserPK", "FirstName", "LastName", DepartmentFK=departmentfk, Enabled=1
            )
        else:
            user = self.user_table.get("UserPK", "FirstName", "LastName")

        if not user:
            raise ValueError("Mie Trak did not return any values. Check last query.")

        for x in user:
            if x:
                user_dict[x[0]] = [x[1], x[2]]
        return user_dict

    def get_quick_view(self):
        quick_view_dict = {}
        quick_view = self.quick_view_table.get("QuickViewPK", "Description")
        if quick_view:
            for x in quick_view:
                quick_view_dict[x[0]] = x[1]
        return quick_view_dict
    
    def add_quick_view_user(self, quick_view_pk, user_fk):
        pk = self.quick_view_users_table.get("QuickViewUserPK", UserFK=user_fk, QuickViewFK=quick_view_pk)
        if not pk:
            info_dict = {
                "QuickViewFK": quick_view_pk,
                "UserFK": user_fk
            }
            pk = self.quick_view_users_table.insert(info_dict)
        return pk
    
    def get_dashboard(self):
        dashboard_dict = {}
        dashboard = self.dashboard_table.get("DashboardPK", "Description")
        if dashboard:
            for x in dashboard:
                dashboard_dict[x[0]] = x[1]
        return dashboard_dict
    
    def add_dashboard_user(self, dashboard_pk, user_fk):
        pk = self.dashboard_user_table.get("DashboardUserPK", DashboardFK=dashboard_pk, UserFK = user_fk)
        if not pk:
            info_dict = {
                "DashboardFK": dashboard_pk,
                "UserFK": user_fk
            }
            pk= self.dashboard_user_table.insert(info_dict)
        return pk

    def get_vacation_request_data(self, date):
        user_data_dict = self.get_user_data(enabled=1)
        vacation_request_dict = {}
        vacation_request_data = self.vacation_request_table.get("VacationRequestPK", "EmployeeFK", "FromDate", "ToDate", "StartTime", "Hours", "Reason", "Approved")
        if vacation_request_data:
            for x in vacation_request_data:
                approved_status = ['Yes' if x[7]==1 else 'No']
                if x[1]:
                    if x[1] in user_data_dict.keys():
                        fn, ln = user_data_dict[x[1]]
                        name = f"{fn} {ln}"

                if x[2] is not None and x[2] >= date:
                    vacation_request_dict[x[0]] = [name, x[2], x[3], x[4], x[5], x[6], approved_status]
        return vacation_request_dict
    
    def get_user_dashboards(self, userpk):
        user_accessed_dashboard = self.dashboard_user_table.get("DashboardFK", UserFK= userpk)
        dashboards = {}
        if user_accessed_dashboard:
            for dashboard_pk in user_accessed_dashboard:
                dashboard_name = self.dashboard_table.get("Description", DashboardPK= dashboard_pk[0])
                if dashboard_name:  # Check if a result is returned
                    dashboards[dashboard_pk[0]] = dashboard_name[0][0]
        
        return dashboards
    
    def get_user_quick_view(self, userpk):
        user_quick_view = self.quick_view_users_table.get("QuickViewFK", UserFK=userpk)
        quick_view = {}
        if user_quick_view:
            for quick_view_fk in user_quick_view:
                quick_view_name = self.quick_view_table.get("Description", QuickViewPK=quick_view_fk[0])
                if quick_view_name:
                    quick_view[quick_view_fk[0]] = quick_view_name[0][0]
        
        return quick_view
    
    def approve_vacation_request(self, vacation_request_pk):
        self.vacation_request_table.update(vacation_request_pk, Approved=1)
    
    def remove_quick_view_access(self, userfk, quickviewfk):
        quick_view_user_fk = self.quick_view_users_table.get("QuickViewUserPK", UserFK=userfk, QuickViewFK=quickviewfk)[0][0]
        if quick_view_user_fk:
            self.quick_view_users_table.delete(quick_view_user_fk)
    
    def remove_dashboard_access(self, userfk, dashboardfk):
        dashboard_user_fk = self.dashboard_user_table.get("DashboardUserPK", UserFK=userfk, DashboardFK=dashboardfk)[0][0]
        if dashboard_user_fk:
            self.dashboard_user_table.delete(dashboard_user_fk)
    
    def get_department(self):
        """Returns all the Department data in the form of a dict with DepartmentPK as Key and Name as value"""
        department_dict = {}
        departments = self.department_table.get("DepartmentPK", "Name")
        if departments:
            for x in departments:
                if x:
                    department_dict[x[0]] = x[1]
        return department_dict
    
    def department_access_qv(self, access, departmentfk, quick_view_fk):
        user = self.get_user_data(departmentfk=departmentfk)
        if access == "Give":
            for user_pk in user.keys():
                self.add_quick_view_user(quick_view_fk, user_pk)
        elif access == "Remove":
            for user_pk1 in user.keys():
                quick_view_users_pk = self.quick_view_users_table.get(
                    "QuickViewUserPK",
                    QuickViewFK=quick_view_fk,
                    UserFK=user_pk1,
                )
                if quick_view_users_pk:
                    for pk in quick_view_users_pk:
                        self.quick_view_users_table.delete(pk[0])
    
    def department_access_db(self, access, departmentfk, db_fk):
        user = self.get_user_data(departmentfk=departmentfk)
        if access == "Give":
            for user_pk in user.keys():
                self.add_dashboard_user(db_fk, user_pk)
        elif access == "Remove":
            for user_pk1 in user.keys():
                dashboard_users_pk = self.dashboard_user_table.get(
                    "DashboardUserPK",
                    DashboardFK=db_fk,
                    UserFK=user_pk1,
                )
                if dashboard_users_pk:
                    for pk in dashboard_users_pk:
                        self.dashboard_user_table.delete(pk[0])
    
    def get_department_user(self, departmentfk):
        """Returns the users of a department in the form of a dict"""
        user = self.get_user_data(departmentfk=departmentfk)
        return user

    def maintain_dept_access_qv(self, dept_qv):
        for key, value in dept_qv.items():
            for qv_pk in value:
                self.department_access_qv("Give", key, qv_pk)      
    
    def maintain_dept_access_db(self, dept_db):
        for key, value in dept_db.items():
            for db_pk in value:
                self.department_access_db("Give", key, db_pk)
    
    def get_user_credentials(self):
        """Returns the user credentials in the form of a dict"""
        user_credentials = {}
        users = self.user_table.get("Code", "Password")
        if users:
            for x in users:
                if x:
                    user_credentials[x[0]] = x[1]
        return user_credentials

    def login_check(self, code, password):
        """Checks if the user credentials are correct"""
        user_credentials = self.get_user_credentials()
        accessable_user = ["32028", "60009", "10000", "31078"]
        if code in accessable_user:
            if user_credentials[code] == password:
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    m = MieTrak()
    print(m.get_user_quick_view(1527))
