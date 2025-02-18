import tkinter as tk
from tkinter import ttk
from typing import Dict
from scripts.controller import Controller
from gui.vacation_request import VacationRequestsWindow, center_window
from gui.add_popup import AddView
from gui.login_window import LoginWindow
from scripts import mie_trak_funcs
from tkinter import messagebox


LOGIN_STATUS = True


def change_login_status():
    global LOGIN_STATUS
    LOGIN_STATUS = True


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Tkinter GUI")
        self.configure(bg="#f4f4f4")  # Light grey background
        # self.geometry("600x500")  # Increased window size
        center_window(self)

        self.withdraw()

        self.login_window = LoginWindow(change_login_status)
        center_window(self.login_window, width=350, height=200)
        self.login_window.focus()
        self.wait_window(self.login_window)

        if LOGIN_STATUS:
            self.deiconify()

            # Configure grid layout to be flexible
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(1, weight=1)
            self.rowconfigure(2, weight=1)

            # Define styles
            style = ttk.Style()
            style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
            style.configure("TLabel", background="#f4f4f4", font=("Arial", 12))
            style.configure("TCombobox", padding=5)

            # Main Frame
            frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="ridge", bd=2)
            frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)

            # Heading
            self.heading = tk.Label(frame, text="Doc Control", font=("Arial", 16, "bold"), bg="#ffffff")
            self.heading.pack(pady=10)

            # Subframes for alignment
            self.subframe1 = tk.Frame(self, bg="#f4f4f4")
            self.subframe1.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
            self.subframe1.columnconfigure(0, weight=1)
            self.subframe1.rowconfigure(1, weight=1)

            self.subframe2 = tk.Frame(self, bg="#f4f4f4")
            self.subframe2.grid(row=1, column=1, padx=15, pady=5, sticky="nsew")
            self.subframe2.columnconfigure(0, weight=1)
            self.subframe2.rowconfigure(1, weight=1)

            # Subheadings
            self.users_label = ttk.Label(self.subframe1, text="Users", font=("Arial", 12, "bold"))
            self.users_label.pack()

            self.dashboards_label = ttk.Label(self.subframe2, text="Accessed Dashboards", font=("Arial", 12, "bold"))
            self.dashboards_label.pack()

            # Comboboxes
            self.combo1 = ttk.Combobox(self.subframe1, values=["User", "Department"], state="readonly")
            self.combo1.pack(pady=5)
            self.combo1.bind("<<ComboboxSelected>>", self.update_with_users_or_department)

            self.combo2 = ttk.Combobox(self.subframe2, values=["Dashboards", "QuickViews"], state="readonly")
            self.combo2.pack(pady=5)
            self.combo2.bind("<<ComboboxSelected>>", self.show_accessed_dashboards_quickview)
            self.combo2.set("Dashboards")

            # Listboxes
            self.user_department_listbox = tk.Listbox(self.subframe1, exportselection=False, relief="solid", bd=1)
            self.user_department_listbox.pack(pady=5, fill="both", expand=True)
            self.user_department_listbox.bind("<<ListboxSelect>>", self.show_accessed_dashboards_quickview)

            self.listbox2 = tk.Listbox(self.subframe2, relief="solid", bd=1)
            self.listbox2.pack(pady=5, fill="both", expand=True)

            # Buttons
            self.button_frame = tk.Frame(self, bg="#f4f4f4")
            self.button_frame.grid(row=2, column=0, columnspan=1, pady=10, sticky="nsew")

            self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_item)
            self.add_button.grid(row=0, column=0, padx=10)

            self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_item)
            self.delete_button.grid(row=0, column=1, padx=10)

            self.vac_req_btn_frame = tk.Frame(self, bg="#f4f4f4")
            self.vac_req_btn_frame.grid(row=2, column=1, columnspan=1, pady=10, sticky="nsew")

            self.vacation_request_button = ttk.Button(self.vac_req_btn_frame, text="Vacation Requests", command=self.open_vacation_request_tab)
            self.vacation_request_button.grid(row=0, column=0, padx=20, sticky="E")

            self.controller = Controller()
        else:
            self.destroy()


    def update_with_users_or_department(self, event):
        self.user_department_listbox.delete(0, tk.END)
        selection = self.combo1.get()

        if selection == "User":

            # change the heading to user
            self.users_label.config(text="User")

            self.user_data = mie_trak_funcs.get_user_data(enabled=True)
            for _, user_info in self.user_data.items():
                self.user_department_listbox.insert(tk.END, f"{user_info[0]} {user_info[1]}")
        elif selection == "Department":

            # change the heading to department
            self.users_label.config(text="Department")

            self.department_data = mie_trak_funcs.get_all_departments()
            for _, name in self.department_data.items():
                self.user_department_listbox.insert(tk.END, f"{name}")

    def show_accessed_dashboards_quickview(self, event):
        self.listbox2.delete(0, tk.END)

        selection = self.user_department_listbox.curselection()
        if not selection:
            messagebox.showerror(title="Selection Invalid", message="Please select a User/Department from the list to view accessed itmes")
            return

        db_or_qv: str = self.combo2.get()
        user_or_department = "User" if self.combo1.get() == "User" else "Department"

        # update heading with selected type (Dashboards or Quickview) from comboboxo
        self.dashboards_label.config(text=db_or_qv)

        if user_or_department == "User":
            userpk = list(self.user_data.keys())[selection[0]]
            self.data_to_display = mie_trak_funcs.get_user_dashboards(userpk) if db_or_qv == "Dashboards" else mie_trak_funcs.get_user_quick_view(userpk)

        elif user_or_department == "Department":

            department_data: Dict = self.controller.get_department_information_from_cache()
            selected_department_pk = list(department_data.keys())[selection[0]]

            accessed_key = "accessed_dashboards" if db_or_qv == "Dashboards" else "accessed_quickviews"
            self.data_to_display = department_data.get(selected_department_pk, {}).get(accessed_key, {})

        else:
            # message: invalid department
            self.data_to_display = {}


        # NOTE: self.data_to_dislpay gets reassigned everytime the user clicks on the box on the right. 
        # We then use this data to get the PK of the selections when the user wants to delete something.
        # refer delete_item function.

        if self.data_to_display:
            for _, name in self.data_to_display.items():
                self.listbox2.insert(tk.END, name)
        else:
            self.listbox2.insert(tk.END, "N/A")

    def add_item(self):
        # LIVE: 
        user_or_department_type = self.combo1.get()
        department_or_user_selection_index = self.user_department_listbox.curselection()[0]

        if not user_or_department_type or not department_or_user_selection_index:
            messagebox.showerror(title="Selection Error", message="Please select User/Department first and then make a selection from the list before clicking add.")
            return


        if user_or_department_type == "User":
            user_pk = list(self.user_data.keys())[department_or_user_selection_index]
            AddView("User", self.controller, self.show_accessed_dashboards_quickview, user_pk=user_pk)

        elif user_or_department_type == "Department":
            department_data_dict = self.controller.get_department_information_from_cache()

            department_pk = list(department_data_dict.keys())[department_or_user_selection_index]
            department_name = department_data_dict.get(department_pk, {}).get("name", {})

            if not department_name:
                messagebox.showerror(title="Department Name Error", message="Department Name could not be resolved, contact developer.")
                return

            AddView(department_name, self.controller, self.show_accessed_dashboards_quickview, department_pk=department_pk)

        else:
            # display error to the user
            pass

    def delete_item(self):
        user_or_department_type = self.combo1.get()
        department_or_user_selection_index = self.user_department_listbox.curselection()

        if not user_or_department_type or not department_or_user_selection_index:
            messagebox.showerror(title="Selection Error", message="Please select User/Department first and then make a selection from the list before clicking delete.")
            return

        db_or_qv = self.combo2.get()
        selected_dashboards_or_qv_indices = self.listbox2.curselection()

        if not selected_dashboards_or_qv_indices or not db_or_qv:
            messagebox.showerror(title="Selection Error", message="Must select dashboards or quickviews to delete")
            return

        dashboard_or_quickview_pks = [list(self.data_to_display.keys())[idx] for idx in selected_dashboards_or_qv_indices]

        if user_or_department_type == "User":
            print("Deleting from user...")
            user_pk = list(self.user_data.keys())[department_or_user_selection_index[0]]

            if db_or_qv == "Dashboards":
                for dashboard_pk in dashboard_or_quickview_pks:
                    mie_trak_funcs.delete_dashboard_from_user(user_pk, dashboard_pk)

            elif db_or_qv == "QuickViews":
                quickview_pks = [list(self.data_to_display.keys())[idx] for idx in selected_dashboards_or_qv_indices]
                for quickview_pk in quickview_pks:
                    mie_trak_funcs.delete_quickview_from_user(user_pk, quickview_pk)

        elif user_or_department_type == "Department":
            print("Deleting from department...")

            department_data_dict = self.controller.get_department_information_from_cache()
            department_pk = list(department_data_dict.keys())[department_or_user_selection_index[0]]  # user selected

            if db_or_qv == "Dashboards":
                for pk in dashboard_or_quickview_pks:
                    self.controller.delete_dashboard_from_department(department_pk, pk)

            elif db_or_qv == "QuickViews":
                for pk in dashboard_or_quickview_pks:
                    self.controller.delete_quickview_from_user(department_pk, pk)

        else:
            # error
            pass

        self.show_accessed_dashboards_quickview(None)  # refresh by fetching data from Mie Trak again

    def open_vacation_request_tab(self):
        data = mie_trak_funcs.get_all_vacation_requests()
        self.withdraw()
        self.vacation_request_window = VacationRequestsWindow(self, data)
        self.vacation_request_window.focus()
        self.wait_window(self.vacation_request_window)
        self.deiconify()
