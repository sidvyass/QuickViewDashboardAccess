import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Dict


class AddView(tk.Toplevel):
    def __init__(self, title: str, controller, call_back_update, department_pk: int | None = None, user_pk: int | None = None):
        super().__init__()
        self.call_back_update = call_back_update
        self.controller = controller
        self.department_pk = department_pk 
        self.user_pk = user_pk
        self.title(title)
        self.geometry("400x300")
        self.configure(bg="#f4f4f4")  # Light gray background
        self.resizable(True, True)
        self.build_widgets()

        print(f"Init complete with - Department PK: {self.department_pk}\nUser PK: {self.user_pk}")

    def build_widgets(self):
        # Configure grid weights for flexibility
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        # Listbox Frame
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # Label
        label = ttk.Label(frame, text="Select Items:", font=("Arial", 12, "bold"))
        label.pack(pady=(0, 5), anchor="w")

        # Listbox with multi-selection
        self.listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, height=10)
        self.listbox.pack(fill="both", expand=True)

        # Buttons Frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=10, sticky="sew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Confirm Button
        confirm_button = ttk.Button(button_frame, text="Confirm", command=self.confirm_selection)
        confirm_button.grid(row=0, column=0, padx=5, sticky="ew")

        # Cancel Button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.dashboards_dict = self.controller.get_all_dashboards()

        self.populate_list(self.dashboards_dict)

    def populate_list(self, data_dict: Dict[int, str]):
        """Populate the listbox with items."""
        self.listbox.delete(0, tk.END)
        for dashboardpk, description in data_dict.items():
            self.listbox.insert(tk.END, description)

    def confirm_selection(self):
        """Handle confirm button click."""
        selected_indices = self.listbox.curselection()

        # find the selected dashboards and their pks
        self.selected_dashboard_pks = []
        i = 0
        for dashboardpk, description in self.dashboards_dict.items():
            if i in selected_indices:
                self.selected_dashboard_pks.append((dashboardpk, description))

        # give dashboard access to all users in the department
        for pk, _ in self.selected_dashboard_pks:
            self.controller.add_dashboard_to_department(self.department_pk, pk)
            break

        self.call_back_update(event=None)  # main GUI function to update the listboxes with the new data

        self.destroy()
