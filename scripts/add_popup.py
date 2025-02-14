import tkinter as tk
from tkinter import ttk
from typing import Dict
from scripts import mie_trak_funcs
from pprint import pprint


class AddView(tk.Toplevel):
    def __init__(self, title: str, controller, call_back_update, department_pk: int | None = None, user_pk: int | None = None):
        super().__init__()
        self.call_back_update = call_back_update
        self.controller = controller
        self.department_pk = department_pk
        self.user_pk = user_pk
        self.title(title)
        self.geometry("500x350")  # Adjusted size for new UI
        self.configure(bg="#f4f4f4")  # Light gray background
        self.resizable(True, True)

        self.dashboards_dict = mie_trak_funcs.get_all_dashboards()
        self.quickviews_dict = mie_trak_funcs.get_all_quickviews()  # Assuming a function for Quickviews

        department_dict = self.controller.cache_dict.get(department_pk, {})

        if department_pk:
            self.accessed_dashboards_pk_dict = department_dict.get("accessed_dashboards", {})
            for key in self.accessed_dashboards_pk_dict.keys():
                del self.dashboards_dict[key]

            self.accessed_quickviews_pk_dict = department_dict.get("accessed_quickviews", {})
            for key in self.accessed_quickviews_pk_dict.keys():
                del self.quickviews_dict[key]

        self.build_widgets()

    def build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        dashboard_label = ttk.Label(self, text="Dashboards", font=("Arial", 12, "bold"))
        dashboard_label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

        quickview_label = ttk.Label(self, text="Quickviews", font=("Arial", 12, "bold"))
        quickview_label.grid(row=0, column=1, pady=(10, 5), padx=10, sticky="w")

        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        self.dashboard_listbox = tk.Listbox(left_frame, selectmode=tk.MULTIPLE, exportselection=False, height=10)
        self.dashboard_listbox.pack(fill="both", expand=True)

        self.quickview_listbox = tk.Listbox(right_frame, selectmode=tk.MULTIPLE, exportselection=False, height=10)
        self.quickview_listbox.pack(fill="both", expand=True)

        self.populate_list(self.dashboard_listbox, self.dashboards_dict)
        self.populate_list(self.quickview_listbox, self.quickviews_dict)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="sew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        confirm_button = ttk.Button(button_frame, text="Confirm", command=self.confirm_selection)
        confirm_button.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

    def populate_list(self, listbox: tk.Listbox, data_dict: Dict[int, str]):
        """Populate a given listbox with items."""
        listbox.delete(0, tk.END)
        for _, description in data_dict.items():
            listbox.insert(tk.END, description)

    def confirm_selection(self):
        """Handle confirm button click."""
        selected_dashboard_indices = self.dashboard_listbox.curselection()
        selected_quickview_indices = self.quickview_listbox.curselection()

        selected_dashboards = [list(self.dashboards_dict.keys())[i] for i in selected_dashboard_indices]
        selected_quickviews = [list(self.quickviews_dict.keys())[i] for i in selected_quickview_indices]

        # Assign selected dashboards
        for dashboard_pk in selected_dashboards:
            self.controller.add_dashboard_to_department(self.department_pk, dashboard_pk)

        # Assign selected quickviews (Assuming a function exists)
        for quickview_pk in selected_quickviews:
            self.controller.add_quickview_to_department(self.department_pk, quickview_pk)

        self.call_back_update(event=None)  # Update main UI
        self.destroy()

