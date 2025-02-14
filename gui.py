import tkinter as tk
from tkinter import ttk
from mie_trak import MieTrak
from typing import Dict, List, Tuple
from controller import Controller
from pprint import pprint
from scripts.add_popup import AddView


class SimpleTkinterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Tkinter GUI")
        self.root.configure(bg="#f4f4f4")  # Light grey background
        self.root.geometry("600x500")  # Increased window size

        # Configure grid layout to be flexible
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Define styles
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
        style.configure("TLabel", background="#f4f4f4", font=("Arial", 12))
        style.configure("TCombobox", padding=5)

        # Main Frame
        frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20, relief="ridge", bd=2)
        frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)

        # Heading
        self.heading = tk.Label(frame, text="Doc Control", font=("Arial", 16, "bold"), bg="#ffffff")
        self.heading.pack(pady=10)

        # Subframes for alignment
        self.subframe1 = tk.Frame(root, bg="#f4f4f4")
        self.subframe1.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.subframe1.columnconfigure(0, weight=1)
        self.subframe1.rowconfigure(1, weight=1)

        self.subframe2 = tk.Frame(root, bg="#f4f4f4")
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

        # Listboxes
        self.user_department_listbox = tk.Listbox(self.subframe1, exportselection=False, relief="solid", bd=1)
        self.user_department_listbox.pack(pady=5, fill="both", expand=True)
        self.user_department_listbox.bind("<<ListboxSelect>>", self.show_accessed_dashboards_quickview)

        self.listbox2 = tk.Listbox(self.subframe2, relief="solid", bd=1)
        self.listbox2.pack(pady=5, fill="both", expand=True)

        # Buttons
        self.button_frame = tk.Frame(root, bg="#f4f4f4")
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")

        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_item)
        self.add_button.grid(row=0, column=0, padx=10)

        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_item)
        self.delete_button.grid(row=0, column=1, padx=10)

        self.mie_trak = MieTrak()

        self.controller = Controller()

    def update_with_users_or_department(self, event):
        self.user_department_listbox.delete(0, tk.END)
        selection = self.combo1.get()

        if selection == "User":
            self.user_data = self.mie_trak.get_user_data(enabled=True)
            for userpk, user_info in self.user_data.items():
                self.user_department_listbox.insert(tk.END, f"{user_info[0]} {user_info[1]}")
        elif selection == "Department":
            self.department_data = self.mie_trak.get_department()
            for departmentpk, name in self.department_data.items():
                self.user_department_listbox.insert(tk.END, f"{name}")

    def show_accessed_dashboards_quickview(self, event):

        # NOTE: Could move a lot of these to the controller.

        self.listbox2.delete(0, tk.END)
        user_or_department = "User" if self.combo1.get() == "User" else "Department"
        selection = self.user_department_listbox.curselection()
        db_or_qv: str = self.combo2.get()

        # need to write a clause for multiple selection.

        if not selection:
            return

        def key_for_index_dict(index_to_find: int, data_dict: Dict):
            i = 0
            for userpk, values in data_dict.items():
                if i == index_to_find:
                    return userpk
                i += 1

        if user_or_department == "User":
            userpk = key_for_index_dict(selection[0], self.user_data)
            data = self.mie_trak.get_user_dashboards(userpk) if db_or_qv == "Dashboards" else self.mie_trak.get_user_quick_view(userpk)
            self.user_to_dash_qv = {userpk: {self.combo2.get(): []}}
            for pk, name in data.items():
                # make a data dict to store the values in, we need to only update it once.
                self.user_to_dash_qv[userpk][db_or_qv].append((pk, name))
                self.listbox2.insert(tk.END, name)

        elif user_or_department == "Department":
            department_data: Dict = self.controller.get_department_information_from_cache()
            department_key_to_find = key_for_index_dict(selection[0], department_data)
            for departmentpk, value_dict in department_data.items():
                if departmentpk == department_key_to_find:
                    accessed_dashboards: Dict = value_dict.get("accessed_dashboards", {}) if db_or_qv != "QuickViews" else value_dict.get("accessed_quickviews", {})
                    if accessed_dashboards:
                        for dashboardpk, name in accessed_dashboards.items():
                            self.listbox2.insert(tk.END, name)
                    else:
                        self.listbox2.insert(tk.END, "Nothing mapped here")

    def add_item(self):
        # LIVE: 
        user_or_department_type = self.combo1.get()
        department_or_user_selection = self.user_department_listbox.curselection()

        if not user_or_department_type:
            # message box to show error
            pass

        if not department_or_user_selection:
            # message box to show error
            pass

        if user_or_department_type == "Department":
            i = 0
            department_data_dict = self.controller.get_department_information_from_cache()
            for department_pk, values in department_data_dict.items():  # loop to find the index value selected by user.
                if i == department_or_user_selection[0]:
                     AddView(values.get("name"), self.controller, self.show_accessed_dashboards_quickview, department_pk=department_pk)
                i += 1
        # TEST:
        # AddView("test", self.controller, department_pk=6)

        if user_or_department_type == "User":
            # TODO:
            pass

    def delete_item(self):
        if self.user_department_listbox.curselection():
            self.user_department_listbox.delete(self.user_department_listbox.curselection())
        if self.listbox2.curselection():
            self.listbox2.delete(self.listbox2.curselection())

        # TODO: Delete from database


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTkinterGUI(root)
    root.mainloop()

