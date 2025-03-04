from tkinter import ttk
import tkinter as tk
from gui.utils import center_window, gui_error_handler
from scripts import mie_trak_funcs
from base_logger import getlogger


LOGGER = getlogger("Create Doc Group")


class CreateDocGroup(tk.Toplevel):
    def __init__(self, callback):
        super().__init__()

        self.title("Create Document Group")
        center_window(self, width=420, height=700)
        self.configure(bg="#f4f4f4")
        self.call_back_update = callback

        self._build_widgets()

    def _build_widgets(self):
        # Grid Configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=0)  # Listbox expands
        self.rowconfigure(2, weight=1)  # Buttons row
        self.rowconfigure(3, weight=0)

        # Code Entry
        self.code_label = ttk.Label(self, text="Code:")
        self.code_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.code_entry = ttk.Entry(self)
        self.code_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Name Entry
        self.name_label = ttk.Label(self, text="Name:")
        self.name_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        # Listbox
        self.listbox = tk.Listbox(self, selectmode="multiple", exportselection=False)

        # Listbox Heading
        self.listbox_label = ttk.Label(
            self, text="Select Users for Document Group", font=("Arial", 10, "bold")
        )
        self.listbox_label.grid(
            row=1, column=0, columnspan=4, padx=10, pady=(5, 0), sticky="w"
        )

        # Adjust Listbox Row
        self.listbox.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        self.users = mie_trak_funcs.get_user_data()

        # Populate Listbox
        for firstname, lastname in self.users.values():
            self.listbox.insert(tk.END, f"{firstname} {lastname}")

        # Button Frame
        self.button_frame = tk.Frame(self, bg="#f4f4f4")
        self.button_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        # Confirm Button
        self.confirm_button = ttk.Button(
            self.button_frame, text="Confirm", command=self.confirm
        )
        self.confirm_button.grid(row=0, column=0, padx=10, sticky="ew")

        # Cancel Button
        self.cancel_button = ttk.Button(
            self.button_frame, text="Cancel", command=self.destroy
        )
        self.cancel_button.grid(row=0, column=1, padx=10, sticky="ew")

    @gui_error_handler
    def confirm(self):
        new_code = self.code_entry.get()
        new_name = self.name_entry.get()

        selected_user_indices = self.listbox.curselection()

        selected_users_pks = [
            list(self.users.keys())[idx] for idx in selected_user_indices
        ]

        inserted_doc_group_pk = mie_trak_funcs.create_document_group(new_code, new_name)

        for userpk in selected_users_pks:
            mie_trak_funcs.add_document_group_to_user(inserted_doc_group_pk, userpk)

        self.call_back_update(event=None)
        self.destroy()
