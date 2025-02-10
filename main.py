import tkinter as tk
from tkinter import font
from mie_trak import MieTrak
from tkinter import messagebox, ttk
from datetime import datetime
import re
import json
from mt_api.base_logger import getlogger
from scripts.dashboard_access import get_all_dashboards


LOGGER = getlogger("main")


# class LoginScreen(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Login Screen")
#         self.geometry("300x200")
#         self.database_conn = MieTrak()
#         # Create widgets
#         self.create_widgets()
#
#     def create_widgets(self):
#         # Username label and entry
#         self.username_label = tk.Label(self, text="Username:")
#         self.username_label.pack(pady=5)
#
#         self.username_entry = tk.Entry(self)
#         self.username_entry.pack(pady=5)
#
#         # Password label and entry
#         self.password_label = tk.Label(self, text="Password:")
#         self.password_label.pack(pady=5)
#
#         self.password_entry = tk.Entry(self, show="*")
#         self.password_entry.pack(pady=5)
#         self.password_entry.bind("<Return>", self.login_check)
#
#         # Login button
#         self.login_button = tk.Button(self, text="Login", command=self.login_check)
#         self.login_button.pack(pady=10)
#
#     def login_check(self, event=None):
#         username = self.username_entry.get()
#         password = self.password_entry.get()
#
#         login_succes_or_not = self.database_conn.login_check(username, password)
#
#         if login_succes_or_not is True:
#             # messagebox.showinfo("Login", "Login successful!")
#             self.destroy()
#             app1 = QuickViewAndDashboard()
#             app1.mainloop()
#         else:
#             messagebox.showerror("Login", "Invalid credentials")


class QuickViewAndDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quick View And Dashboard Access")
        self.geometry("500x200")
        self.database_conn = MieTrak()
        self.user_data_dict = self.database_conn.get_user_data(enabled=1)
        self.user_data_list = [(value[0], value[1]) for value in self.user_data_dict.values()]
        self.user_display_list = [f"{firstname} {lastname}" for firstname, lastname in self.user_data_list]
        self.user_display_list = sorted(self.user_display_list)
        self.quick_view_dict = self.database_conn.get_quick_view()
        self.quick_view_list = [f"{value} PK:{key}" for key,value in self.quick_view_dict.items()]
        self.quick_view_list = sorted(self.quick_view_list)
        self.dashboards_dict = self.database_conn.get_dashboard()
        self.dashboards_list = [f"{value} PK:{key}" for key,value in self.dashboards_dict.items()]
        self.dashboards_list = sorted(self.dashboards_list)
        self.department_dict = self.database_conn.get_department()
        self.department_names = list(self.department_dict.values())
        self.department_data_list = [(v, k) for k, v in self.department_dict.items()]
        self.department_display_list = [
            f"{name} PK:{pk}" for name, pk in self.department_data_list
        ]

        self.combobox()

    def combobox(self):
        self.heading_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=12)

        heading_label = tk.Label(self, text='Dashboard Access App', font=self.heading_font)
        heading_label.grid(row=0, column=0, columnspan=3, sticky="NSEW")

        button1 = tk.Button(self, text="Quick View Access", font=self.button_font, command=self.quick_view_access)
        button1.grid(row=1, column=0, sticky='EW', padx=10)

        button2 = tk.Button(self, text="Dashboard Access", font=self.button_font, command=self.dashboard_access)
        button2.grid(row=1, column=1, sticky='EW', padx=10)

        button3 = tk.Button(self, text="Vacation Request", font=self.button_font, command=self.vacation_request)
        button3.grid(row=1, column=2, sticky='EW', padx=10)

        button4 = tk.Button(self, text="Quick View Department", font=self.button_font, command=self.quick_view_access_by_department)
        button4.grid(row=2, column=0, sticky='EW', padx=10)

        button5 = tk.Button(self, text = "Dashboard Department", font=self.button_font, command=self.dashboard_access_by_department)
        button5.grid(row=2, column=1, sticky='EW', padx=10)

        button6 = tk.Button(self, text="Multiple Department", font =self.button_font, command=self.multiple_department)
        button6.grid(row=2, column=2, sticky='EW', padx=10)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        for i in range(3):
            self.columnconfigure(i, weight=1)

    
    def quick_view_access(self):
        self.open_new_window("QuickViewAccess")
    
    def dashboard_access(self):
        self.open_new_window("DashboardAccess")
    
    def vacation_request(self):
        self.open_new_window("VacationRequest")
    
    def quick_view_access_by_department(self):
        self.open_new_window("QuickViewDepartment")
    
    def dashboard_access_by_department(self):
        self.open_new_window("DashboardDepartment")
    
    def multiple_department(self):
        self.open_new_window("MultipleDepartment")

    def open_new_window(self, title):
        new_window = tk.Toplevel(self)
        new_window.title(title)
        new_window.grab_set()

        if title == "QuickViewAccess":
            new_window.geometry("700x500")  # Adjust width for additional gridbox

            heading_label = tk.Label(new_window, text='Quick View Access', font=self.heading_font)
            heading_label.grid(row=0, column=0, columnspan=6, sticky="NSEW")

            user_box_label = tk.Label(new_window, text='Select User', font=self.button_font)
            user_box_label.grid(row=1, column=0, columnspan=2, padx=5, sticky="NSEW")
            self.multi_user_listbox = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.multi_user_listbox.grid(row=2, column=0, columnspan=2, padx=5, sticky="NSEW")
            for user in self.user_display_list:
                self.multi_user_listbox.insert(tk.END, user)

            quick_view_label = tk.Label(new_window, text='Select Quick View', font=self.button_font)
            quick_view_label.grid(row=1, column=2, columnspan=2, padx=5, sticky="NSEW")
            self.quick_view_listbox = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.quick_view_listbox.grid(row=2, column=2, columnspan=2, padx=5, sticky="NSEW")
            for item in self.quick_view_list:
                self.quick_view_listbox.insert(tk.END, item)

            # New label and Listbox for Accessed QuickViews
            accessed_label = tk.Label(new_window, text='Accessed Quick Views', font=self.button_font)
            accessed_label.grid(row=1, column=4, columnspan=2, padx=5, sticky="NSEW")
            self.accessed_quick_view_listbox = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.accessed_quick_view_listbox.grid(row=2, column=4, columnspan=2, padx=5, sticky="NSEW")

            button = tk.Button(new_window, text="Give Quick View Access", font=self.button_font, command=lambda: self.give_access("quick_view"))
            button.grid(row=3, column=0, columnspan=6, sticky="NSEW")

            button1 = tk.Button(new_window, text="Remove Access", font=self.button_font, command=lambda: self.remove_access("quick_view"))
            button1.grid(row=4, column=0, columnspan=6, sticky="NSEW")
            new_window.rowconfigure(0, weight=1)
            new_window.rowconfigure(1, weight=1)
            new_window.rowconfigure(2, weight=2)
            new_window.rowconfigure(3, weight=1)
            new_window.rowconfigure(4, weight=1)

            self.multi_user_listbox.bind("<<ListboxSelect>>", self.currentlyAccessedQuickView)

            for column in range(6):
                new_window.columnconfigure(column, weight=1)


        elif title == "DashboardAccess":
            new_window.geometry("700x500")

            heading_label = tk.Label(new_window, text='Dashboard Access', font=self.heading_font)
            heading_label.grid(row=0, column=0, columnspan=6, sticky="NSEW")

            user_label = tk.Label(new_window, text='Select User', font=self.button_font)
            user_label.grid(row=1, column=0, columnspan=2, padx=5, sticky="NSEW")
            self.multi_user_listbox1 = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.multi_user_listbox1.grid(row=2, column=0, columnspan=2, padx=5, sticky="NSEW")
            for user in self.user_display_list:
                self.multi_user_listbox1.insert(tk.END, user)

            user_label = tk.Label(new_window, text='Select Dashboard', font=self.button_font)
            user_label.grid(row=1, column=2, columnspan=2, padx=5, sticky="NSEW")
            self.dashboard_listbox = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.dashboard_listbox.grid(row=2, column=2, columnspan=2, padx=5, sticky="NSEW")
            for dashboard in self.dashboards_list:
                self.dashboard_listbox.insert(tk.END, dashboard)

            accessed_label = tk.Label(new_window, text='Accessed Dashboards', font=self.button_font)
            accessed_label.grid(row=1, column=4, columnspan=2, padx=5, sticky="NSEW")
            self.accessed_dashboard_listbox = tk.Listbox(
                new_window,
                height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED,
            )
            self.accessed_dashboard_listbox.grid(row=2, column=4, columnspan=2, padx=5, sticky="NSEW")
            
            button = tk.Button(new_window, text="Give Dashboard Access", font=self.button_font, command= lambda: self.give_access("dashboard"))
            button.grid(row=3, column=0, columnspan=6, sticky="NSEW")

            button1 = tk.Button(new_window, text="Remove Access", font=self.button_font, command=lambda: self.remove_access("dashboard"))
            button1.grid(row=4, column=0, columnspan=6, sticky="NSEW")

            new_window.rowconfigure(0, weight=1)
            new_window.rowconfigure(1, weight=1)
            new_window.rowconfigure(2, weight=2)
            new_window.rowconfigure(3, weight=1)
            new_window.rowconfigure(4, weight=1)

            self.multi_user_listbox1.bind("<<ListboxSelect>>", self.currentlyAccessedDashboard)

            for column in range(6):
                new_window.columnconfigure(column, weight=1)

        elif title == "VacationRequest":

            self.tree = ttk.Treeview(new_window, columns=('ID', 'Name', 'FromDate', 'ToDate', 'StartTime', 'Hours', 'Reason', 'Approved'), show='headings')
            self.tree.heading('ID', text='ID')
            self.tree.heading('Name', text='Name')
            self.tree.heading('FromDate', text='From Date')
            self.tree.heading('ToDate', text='To Date')
            self.tree.heading('StartTime', text='Start Time')
            self.tree.heading('Hours', text='Hours')
            self.tree.heading('Reason', text='Reason')
            self.tree.heading('Approved', text='Approved')
            # self.tree.heading('VacationRequestType', text='Vacation Request Type') NOTE: Get this done.
            

            self.tree.column('ID', width=50)
            self.tree.column('Name', width=150)
            self.tree.column('FromDate', width=100)
            self.tree.column('ToDate', width=100)
            self.tree.column('StartTime', width=100)
            self.tree.column('Hours', width=100)
            self.tree.column('Reason', width=300)
            self.tree.column('Approved', width=100)

            self.tree.pack(fill=tk.BOTH, expand=True)

            self.approve_button = tk.Button(new_window, text="Approve", command=self.approve_vacation)
            self.approve_button.pack(pady=10)
            
            # Initially disable the button
            self.approve_button.config(state=tk.DISABLED)

            self.populate_table()
        
        elif title == "QuickViewDepartment":
            new_window.geometry("700x500")
            tk.Label(new_window, text="Select Department", font = self.heading_font).grid(row=0, column=0, columnspan =2, sticky="NSEW", padx=5, pady=5)
            self.department_combobox1 = ttk.Combobox(
                new_window, values=sorted(self.department_display_list) , state="normal", font=self.button_font,
            ) 
            
            self.department_combobox1.grid(row=1, column=0, columnspan=2, sticky = "SN", padx=5, pady=5) 
            tk.Label(new_window, text = "Quick View", font=self.button_font).grid(row=2, column=0, columnspan =2, sticky="NSEW", padx=5)
            self.quick_view_combobox = tk.Listbox(new_window, height = 10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.quick_view_combobox.grid(row=3, column=0, columnspan=2, sticky="NSEW", padx=5)
            for item in self.quick_view_list:
                self.quick_view_combobox.insert(tk.END, item)
            tk.Label(new_window, text = "Mapped Quick View", font = self.button_font).grid(row=2, column=2, columnspan=2, padx=5)
            self.mapped_quick_view_combobox = tk.Listbox(new_window, height = 10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.mapped_quick_view_combobox.grid(row=3, column=2, columnspan=2, padx=5)
            tk.Label(new_window, text= "User", font=self.button_font).grid(row=2, column=4, columnspan=2, sticky="NSEW", padx=5)
            self.user_combobox1 = tk.Listbox(new_window, height= 10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.user_combobox1.grid(row=3, column=4, columnspan=2, sticky="NSEW",padx=5)
            self.department_combobox1.bind("<<ComboboxSelected>>", self.display_dept_quick_view)
            button = tk.Button(new_window, text="Add Quick View", font=self.button_font, command= lambda: self.add_or_remove_from_quick_view("add"))
            button.grid(row=4, column=0, columnspan=2, sticky="NSEW", padx=5)
            button1 = tk.Button(new_window, text="Remove Quick View", font=self.button_font, command=lambda: self.add_or_remove_from_quick_view("remove"))
            button1.grid(row=4, column=2, columnspan=2, sticky="NSEW", padx=5)
            button2 = tk.Button(new_window, text = "Maintain Department Access", font=self.button_font, command=lambda: self.maintain_dept_access("qv"))
            button2.grid(row=4, column=4, columnspan=2, sticky="NSEW", padx=5)


        elif title == "DashboardDepartment":
            new_window.geometry("700x500")
            tk.Label(new_window, text="Select Department", font = self.heading_font).grid(row=0, column=0, columnspan =4, sticky="NSEW", padx=5, pady=5)
            self.department_combobox = ttk.Combobox(
                new_window, values=sorted(self.department_display_list) , state="normal", font=self.button_font,
            ) 
            self.department_combobox.grid(row=1, column=0, columnspan=2, sticky = "SN", padx=5, pady=5) 
            tk.Label(new_window, text="Dashboard", font=self.button_font).grid(row = 2, column=0, columnspan=2, sticky="NSEW", padx=5, pady=5)
            self.dashboard_combobox = tk.Listbox(new_window, height=10,
                width=30,
                exportselection=False,
                selectmode=tk.EXTENDED, )
            self.dashboard_combobox.grid(row=3, column=0, columnspan=2, sticky="NSEW", padx=5, pady=5)
            for dashboard in self.dashboards_list:
                self.dashboard_combobox.insert(tk.END, dashboard)
            tk.Label(new_window, text= "Mapped Dashboard", font=self.button_font).grid(row=2, column=2, columnspan=2, padx=5)
            self.mapped_dashboard_combobox = tk.Listbox(new_window, height=10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.mapped_dashboard_combobox.grid(row=3, column=2, columnspan=2, sticky="NSEW", padx=5)
            tk.Label(new_window, text= "User", font=self.button_font).grid(row=2, column =4, columnspan=2, sticky="NSEW", padx=5)
            self.user_combobox = tk.Listbox(new_window, height=10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.user_combobox.grid(row=3, column=4, columnspan=2, sticky="NSEW", padx=5)
            self.department_combobox.bind("<<ComboboxSelected>>", self.display_dept_dashboard)
            button = tk.Button(new_window, text="Add Dashboard", font=self.button_font, command= lambda: self.add_or_remove_from_dashboard("add"))
            button.grid(row=4, column=0, columnspan=2, sticky="NSEW", padx=5)
            button1 = tk.Button(new_window, text="Remove Dashboard", font=self.button_font, command= lambda: self.add_or_remove_from_dashboard("remove"))
            button1.grid(row=4, column=2, columnspan=2, sticky="NSEW", padx=5)
            button2 = tk.Button(new_window, text = "Maintain Department Access", font=self.button_font, command = lambda: self.maintain_dept_access("db"))
            button2.grid(row=4, column=4, columnspan=2, sticky="NSEW", padx=5)
        
        elif title == "MultipleDepartment":
            new_window.geometry("700x500")
            tk.Label(new_window, text="Select Department", font = self.button_font).grid(row=0, column=0, columnspan=2, padx=5, sticky="NSEW")
            self.department_lb = tk.Listbox(new_window, height=10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.department_lb.grid(row=1, column=0, columnspan=2, padx=5, sticky="NSEW")
            for department in self.department_display_list:
                self.department_lb.insert(tk.END, department)
            
            tk.Label(new_window, text="Select Dashboard", font = self.button_font).grid(row=0, column =2, columnspan=2, sticky="NSEW", padx=5)
            self.dashboard_lb = tk.Listbox(new_window, height=10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.dashboard_lb.grid(row=1, column=2, columnspan=2, padx=5, sticky="NSEW")

            for dashboard in self.dashboards_list:
                self.dashboard_lb.insert(tk.END, dashboard)
            
            tk.Label(new_window, text="Select QuickView", font = self.button_font).grid(row = 0, column=4, columnspan=2, sticky="NSEW", padx=5)
            self.qv_lb = tk.Listbox(new_window, height=10, width=30, exportselection=False, selectmode=tk.EXTENDED)
            self.qv_lb.grid(row=1, column=4, columnspan=2, padx=5, sticky="NSEW")

            for qv in self.quick_view_list:
                self.qv_lb.insert(tk.END, qv)
            

            button1 = tk.Button(new_window, text="Add Quick View", font=self.button_font, command=lambda: self.multiple_department_mapping("qv"))
            button1.grid(row=2, column=3, columnspan=3, padx=5, sticky="NSEW")
            
            button2 = tk.Button(new_window, text="Add Dashboard", font=self.button_font, command = lambda: self.multiple_department_mapping("db"))
            button2.grid(row=2, column=0, columnspan=3, padx=5, sticky="NSEW")

            button3 = tk.Button(new_window, text = "Maintain Quick View", font = self.button_font, command=lambda: self.maintain_dept_access("qv"))
            button3.grid(row=3, column=0, columnspan=3, padx=5, sticky="NSEW")

            button4 = tk.Button(new_window, font=self.button_font, text="Maintain Dashboard", command=lambda: self.maintain_dept_access("db"))
            button4.grid(row=3, column=3, columnspan=3, padx=5, sticky="NSEW")



    def display_dept_quick_view(self, event):
        self.user_combobox1.delete(0, tk.END)
        self.mapped_quick_view_combobox.delete(0, tk.END)
        dept_qv_dict = self.load_dict()
        selected_dept = self.department_combobox1.get()
        dept_user_list = []
        dept_qv_list = []
        if selected_dept:
            dept_fk = selected_dept.split("PK:")[1]
        department_user = self.database_conn.get_department_user(dept_fk)
        for key2, value2 in department_user.items():
            dept_user_list.append(value2[0] + " " + value2[1])
        for user in sorted(dept_user_list):
            self.user_combobox1.insert(tk.END, user)
        for k,v in dept_qv_dict.items():
            if int(k) == int(dept_fk):
                for qv_fk in v:
                    for key1, value1 in self.quick_view_dict.items():
                        if key1 == qv_fk:
                            dept_qv_list.append(f"{value1} PK:{key1}")
        print(dept_qv_list)
        for dept_qv in sorted(dept_qv_list):
            self.mapped_quick_view_combobox.insert(tk.END, dept_qv)


    def display_dept_dashboard(self, event):
        self.user_combobox.delete(0, tk.END)
        self.mapped_dashboard_combobox.delete(0, tk.END)
        dept_db_dict = self.load_dict1()
        selected_dept = self.department_combobox.get()
        dept_db_list = []
        dept_user_list = []
        if selected_dept:
            dept_fk = selected_dept.split("PK:")[1]
        department_user = self.database_conn.get_department_user(dept_fk)
        for key2, value2 in department_user.items():
            dept_user_list.append(value2[0] + " " + value2[1])
        for user in sorted(dept_user_list):
            self.user_combobox.insert(tk.END, user)
        for k,v in dept_db_dict.items():
            if int(k) == int(dept_fk):
                for db_fk in v:
                    for key1, value1 in self.dashboards_dict.items():
                        if key1 == db_fk:
                            dept_db_list.append(f"{value1} PK:{key1}")
        
        print(dept_db_list)
        for dept_db in dept_db_list:
            self.mapped_dashboard_combobox.insert(tk.END, dept_db)



    def load_dict(self):
        try:
            with open("qv_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def load_dict1(self):
        try:
            with open("db_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    # Save dictionary to JSON file
    def save_dict(self, data):
        with open("qv_data.json", "w") as file:
            json.dump(data, file, indent=4)

    def save_dict1(self, data):
        with open("db_data.json", "w") as file:
            json.dump(data, file, indent=4)

    def multiple_department_mapping(self, type1):
        if type1 == "qv":
            dictionary = self.load_dict()
            selected_dept_ind = self.department_lb.curselection()
            selected_qv_ind =self.qv_lb.curselection()
            if selected_dept_ind:
                for ind in selected_dept_ind:
                    selected_dept = self.department_lb.get(ind)
                    dept_fk = selected_dept.split("PK:")[1]
                    if selected_qv_ind:
                        for ind1 in selected_qv_ind:
                            selected_qv = self.qv_lb.get(ind1)
                            qv_fk = int(selected_qv.split("PK:")[1])
                
                            if qv_fk and dictionary:
                                if qv_fk not in dictionary[dept_fk]:
                                    dictionary[dept_fk].append(qv_fk)
                                self.save_dict(dictionary)
            messagebox.showinfo("Done", "Quick View Mapped")                    
        
        elif type1 == "db":
            dictionary = self.load_dict1()
            selected_dept_ind = self.department_lb.curselection()
            selected_db_ind = self.dashboard_lb.curselection()
            if selected_dept_ind:
                for ind in selected_dept_ind:
                    selected_dept = self.department_lb.get(ind)
                    dept_fk = selected_dept.split("PK:")[1]
                    if selected_db_ind:
                        for ind1 in selected_db_ind:
                            selected_db = self.dashboard_lb.get(ind1)
                            db_fk = int(selected_db.split("PK:")[1])

                            if db_fk and dictionary:
                                if db_fk not in dictionary[dept_fk]:
                                    dictionary[dept_fk].append(db_fk)
                                self.save_dict1(dictionary)
            messagebox.showinfo("Done", "Dashboards Mapped")
        
        self.department_lb.selection_clear(0, tk.END)
        self.dashboard_lb.selection_clear(0, tk.END)
        self.qv_lb.selection_clear(0, tk.END)



    # Add value to list
    def add_value(self, key, new_value):
        # new_value = simpledialog.askstring("Input", f"Enter new value for {key}:")
        dictionary = self.load_dict()
        if new_value and dictionary:
            if new_value not in dictionary[key]:
                dictionary[key].append(new_value)
            self.save_dict(dictionary)
            self.refresh_listbox(dictionary, key)
    
    def add_value1(self, key, new_value):
        # new_value = simpledialog.askstring("Input", f"Enter new value for {key}:")
        dictionary = self.load_dict1()
        if new_value and dictionary:
            if new_value not in dictionary[key]:
                dictionary[key].append(new_value)
            self.save_dict1(dictionary)
            self.refresh_listbox1(dictionary, key)

    # Remove value from list
    def remove_value(self, key, value):
        # value = simpledialog.askstring("Input", f"Enter value to remove from {key}:")
        dictionary = self.load_dict()
        if dictionary and value in dictionary[key]:
            dictionary[key].remove(value)
            self.save_dict(dictionary)
            self.refresh_listbox(dictionary, key)
    
    def remove_value1(self, key, value):
        # value = simpledialog.askstring("Input", f"Enter value to remove from {key}:")
        dictionary = self.load_dict1()
        if dictionary and value in dictionary[key]:
            dictionary[key].remove(value)
            self.save_dict1(dictionary)
            self.refresh_listbox1(dictionary, key)
    
    def refresh_listbox(self, dictionary, selected_department_pk):
        self.mapped_quick_view_combobox.delete(0, tk.END)
        for key, values in dictionary.items():
            if key == selected_department_pk:
                for qv_pk in values:
                    for key1, value1 in self.quick_view_dict.items():
                        if key1 == qv_pk:
                            self.mapped_quick_view_combobox.insert(tk.END, f"{value1} PK:{key1}")
    
    def refresh_listbox1(self, dictionary, selected_department_pk):
        self.mapped_dashboard_combobox.delete(0, tk.END)
        for key, values in dictionary.items():
            if key == selected_department_pk:
                for db_pk in values:
                    for key1, value1 in self.dashboards_dict.items():
                        if key1 == db_pk:
                            self.mapped_dashboard_combobox.insert(tk.END, f"{value1} PK:{key1}")

    def currentlyAccessedQuickView(self, event):
        self.accessed_quick_view_listbox.delete(0,tk.END)
        selected_user_indices = self.multi_user_listbox.curselection()
        for ind in selected_user_indices:
            selected_user = self.multi_user_listbox.get(ind)
            print(selected_user)
            for key, value in self.user_data_dict.items():
                user= " ".join(value)
                # print(user)
                if selected_user == user:
                    print(key)
                    userfk = key
                    accessed_quickView = self.database_conn.get_user_quick_view(userfk)
                    print(accessed_quickView)
                    for pk,qv in accessed_quickView.items():
                        self.accessed_quick_view_listbox.insert(tk.END, f"{user}: {qv} PK:{pk}")
    
    def currentlyAccessedDashboard(self, event):
        self.accessed_dashboard_listbox.delete(0,tk.END)
        selected_user_indices = self.multi_user_listbox1.curselection()
        for ind in selected_user_indices:
            selected_user = self.multi_user_listbox1.get(ind)
            print(selected_user)
            for key, value in self.user_data_dict.items():
                user= " ".join(value)
                # print(user)
                if selected_user == user:
                    print(key)
                    userfk = key
                    dashboard = self.database_conn.get_user_dashboards(userfk)
                    print(dashboard)
                    for pk,db in dashboard.items():
                        self.accessed_dashboard_listbox.insert(tk.END, f"{user}: {db} PK:{pk}")

        # return accessed_quickView
        
        # elif type2 == 'dashboards':
        #     accessed_dashboards = self.database_conn.get_user_dashboards(userfk)
        #     return accessed_dashboards
    
    def add_or_remove_from_quick_view(self, access):
        selected_department = self.department_combobox1.get()
        # for key1, value1 in self.department_dict.items():
        #     if value1 == selected_department:
        pk_to_remove = []
        if selected_department:    
            selected_department_pk = selected_department.split("PK:")[1]
        
        if access == "add":
            selected_indices = self.quick_view_combobox.curselection()
            for index in selected_indices:
                selected_quick_view = self.quick_view_combobox.get(index)
                selected_quick_view_pk = selected_quick_view.split("PK:")[1]
            # for key, value in self.quick_view_dict.items():
            #     if value == selected_quick_view:
            #         selected_doc_group_pk = key
                    # if access == "add":
                self.add_value(
                    str(selected_department_pk), int(selected_quick_view_pk)
                )
        elif access == "remove":
            selected_indices = self.mapped_quick_view_combobox.curselection()
            for index in selected_indices:
                selected_quick_view = self.mapped_quick_view_combobox.get(index)
                selected_quick_view_pk = selected_quick_view.split("PK:")[1]
                pk_to_remove.append(selected_quick_view_pk)
            for pk in pk_to_remove:    
                self.remove_value(str(selected_department_pk), int(pk))

        if access == "add":
            messagebox.showinfo("Done", "Quick View added")
        elif access == "remove":
            messagebox.showinfo("Done", "Quick View removed")
        
        self.quick_view_combobox.selection_clear(0, tk.END)
        self.mapped_quick_view_combobox.selection_clear(0, tk.END)


    def add_or_remove_from_dashboard(self, access):
        selected_dept = self.department_combobox.get()
        pk_to_remove = []
        if selected_dept:
            selected_dept_pk = selected_dept.split("PK:")[1]
        if access == "add":
            selected_indices = self.dashboard_combobox.curselection()
            for index in selected_indices:
                selected_dashboard = self.dashboard_combobox.get(index)
                selected_dashboard_pk = selected_dashboard.split("PK:")[1]
                self.add_value1(str(selected_dept_pk), int(selected_dashboard_pk))
        elif access =="remove":
            selected_indices = self.mapped_dashboard_combobox.curselection()
            for index in selected_indices:
                selected_dashboard = self.mapped_dashboard_combobox.get(index)
                selected_dashboard_pk = selected_dashboard.split("PK:")[1]
                pk_to_remove.append(selected_dashboard_pk)
            for pk in pk_to_remove:
                self.remove_value1(str(selected_dept_pk), int(pk))
        
        if access == "add":
            messagebox.showinfo("Done", "Dashboard added")
        elif access == "remove":
            messagebox.showinfo("Done", "Dashboard removed")
        
        self.dashboard_combobox.selection_clear(0, tk.END)
        self.mapped_dashboard_combobox.selection_clear(0, tk.END)
    
    
    def remove_access(self, type1):
        if type1 == "quick_view":
            selected_indices = self.accessed_quick_view_listbox.curselection()
            for ind in selected_indices:
                selected_qv = self.accessed_quick_view_listbox.get(ind)
                match = re.match(r"(?P<user>.+): (?P<qv>.+) PK:(?P<pk>\d+)", selected_qv)
                if match:
                    selected_user = match.group("user")
                    qv = match.group("qv")
                    qv_pk = int(match.group("pk"))  # Convert pk to an integer if needed
                    print(f"User = {selected_user}, qv = {qv}, pk = {qv_pk}")
                    for key, value in self.user_data_dict.items():
                        user = " ".join(value)
                        if selected_user == user:
                            selected_user_pk = key
                            self.database_conn.remove_quick_view_access(selected_user_pk, qv_pk)
                    
                    self.quick_view_listbox.selection_clear(0, tk.END)
                    self.multi_user_listbox.selection_clear(0, tk.END)
                    self.accessed_quick_view_listbox.delete(0, tk.END)
                    
                    
                    messagebox.showinfo("Done", "Access Removed")

                else:
                    print("String format is incorrect.")
        
        elif type1=="dashboard":
            selected_indices = self.accessed_dashboard_listbox.curselection()
            for ind in selected_indices:
                selected_db = self.accessed_dashboard_listbox.get(ind)
                match = re.match(r"(?P<user>.+): (?P<db>.+) PK:(?P<pk>\d+)", selected_db)
                if match:
                    selected_user = match.group("user")
                    db = match.group("db")
                    db_pk = int(match.group("pk"))  # Convert pk to an integer if needed
                    print(f"User = {selected_user}, db = {db}, pk = {db_pk}")
                    for key, value in self.user_data_dict.items():
                        user = " ".join(value)
                        if selected_user == user:
                            selected_user_pk = key
                            self.database_conn.remove_dashboard_access(selected_user_pk, db_pk)
                    self.dashboard_listbox.selection_clear(0, tk.END)
                    self.multi_user_listbox1.selection_clear(0, tk.END)
                    self.accessed_dashboard_listbox.delete(0, tk.END)
                    messagebox.showinfo("Done", "Access Removed")
                else:
                    print("String format is incorrect.")



    def give_access(self, type1):
        if type1 == "quick_view":
            selected_indices = self.quick_view_listbox.curselection()
            selected_user_indices = self.multi_user_listbox.curselection()
            if not selected_indices and selected_user_indices:
                messagebox.showwarning(
                    "No Selection", "Please select at least one document group and User."
                )
                return
            for index in selected_indices:
                selected_quick_view = self.quick_view_listbox.get(index)
                selected_quick_view_pk = selected_quick_view.split("PK:")[1]
                for ind in selected_user_indices:
                    selected_user = self.multi_user_listbox.get(ind)
                
                    # user_first_name = selected_user.split(" ")[0]
                    # user_last_name = selected_user.split(" ")[1]
                    for key, value in self.user_data_dict.items():
                        user = " ".join(value)
                        if selected_user == user:
                            selected_user_pk = key
                    
                    if selected_quick_view_pk and selected_user_pk:
                        self.database_conn.add_quick_view_user(selected_quick_view_pk, selected_user_pk)
            
            self.quick_view_listbox.selection_clear(0, tk.END)
            self.multi_user_listbox.selection_clear(0, tk.END)
            self.accessed_quick_view_listbox.delete(0, tk.END)
            messagebox.showinfo("Done", "Access Given")
        elif type1 == "dashboard":
            selected_indices = self.dashboard_listbox.curselection()
            selected_user_indices = self.multi_user_listbox1.curselection()
            if not selected_indices and selected_user_indices:
                messagebox.showwarning(
                    "No Selection", "Please select at least one dashboard and User."
                )
                return
            for index in selected_indices:
                selected_dashboard = self.dashboard_listbox.get(index)
                selected_dashboard_pk = selected_dashboard.split("PK:")[1]
                for ind in selected_user_indices:
                    selected_user = self.multi_user_listbox1.get(ind)
                
                    # user_first_name = selected_user.split(" ")[0]
                    # user_last_name = selected_user.split(" ")[1]
                    for key, value in self.user_data_dict.items():
                        user = " ".join(value)
                        if selected_user == user:
                            selected_user_pk1 = key
                    
                    if selected_dashboard_pk and selected_user_pk1:
                        self.database_conn.add_dashboard_user(selected_dashboard_pk, selected_user_pk1)
            self.dashboard_listbox.selection_clear(0, tk.END)
            self.multi_user_listbox1.selection_clear(0, tk.END)
            self.accessed_dashboard_listbox.delete(0,tk.END)
            messagebox.showinfo("Done", "Access Given")
#NOTE: create a function for remove quick view and dashboard

    def populate_table(self):
        vacation_data = self.database_conn.get_vacation_request_data(datetime.now())
        for row in self.tree.get_children():
            self.tree.delete(row)

        for key, values in vacation_data.items():
            self.tree.insert("", "end", values=(key, *values))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
    
    def on_row_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            approved_status = item['values'][7]  # Get "Approved" column value

            # Enable or disable the Approve button based on approval status
            if approved_status == 'Yes':
                self.approve_button.config(state=tk.DISABLED)
            else:
                self.approve_button.config(state=tk.NORMAL)

    def approve_vacation(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            row_id = item['values'][0]  # Get ID from the selected row
            print(f"Approving vacation request with ID: {row_id}")
            # Call your function to approve the request here
            
            self.database_conn.approve_vacation_request(row_id)
            messagebox.showinfo("Approved", f"Vacation Request Approved for {item['values'][1]}")
            
            self.populate_table()
    
    def maintain_dept_access(self, type1):
        
        if type1 =="qv":
            qv_dict = self.load_dict()
            self.database_conn.maintain_dept_access_qv(qv_dict)
        elif type1 == "db":
            db_dict = self.load_dict1()
            self.database_conn.maintain_dept_access_db(db_dict)
        
        messagebox.showinfo("Done", "Access Given")



if __name__ == "__main__":
    # app = LoginScreen()
    # app = QuickViewAndDashboard()
    # app.mainloop()

    from scripts.dashboard_access import assign_user_access_to_dashboards, get_active_users
    from pprint import pprint
    print(len(get_all_dashboards()))
    # assign_user_access_to_dashboards(1571, get_all_dashboards())
