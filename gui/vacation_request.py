import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk, messagebox
from datetime import datetime
from scripts import mie_trak_funcs
from scripts.controller import send_email
from scripts.request_history import RequestHistory
from base_logger import getlogger
from typing import Dict, List
from gui.utils import gui_error_handler, center_window


LOGGER = getlogger("VR Window")


class VacationRequestsWindow(tk.Toplevel):
    """
    A popup window for managing vacation requests, including approval and disapproval.
    """

    def __init__(self, master, data: List[Dict]):
        """
        Initialize the VacationRequestsWindow.

        :param master: The parent widget.
        :param data: A list of dictionaries containing vacation request details.
        """
        super().__init__(master)
        self.title("Vacation Requests")
        center_window(self, width=1500)

        self.data = data
        self.history = RequestHistory()

        self.build_widgets()
        self.refresh_data()

    def build_widgets(self):
        """
        Create and configure widgets for the vacation requests window.
        """
        self.heading_label = ttk.Label(
            self, text="Vacation Requests", font=("Arial", 14, "bold")
        )
        self.heading_label.pack(pady=10)

        columns = (
            "Vacation ID",
            "Employee",
            "From Date",
            "To Date",
            "Start Time",
            "Hours",
            "Reason",
            "Approved",
        )
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", height=10, selectmode="extended"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.approve_button = ttk.Button(
            button_frame, text="Approve", command=self.approve_request
        )
        self.approve_button.grid(row=0, column=0, padx=10)

        self.disapprove_button = ttk.Button(
            button_frame, text="Disapprove", command=self.disapprove_request
        )
        self.disapprove_button.grid(row=0, column=1, padx=10)

        self.history_button = ttk.Button(
            button_frame, text="View Past Requests", command=self.open_history_popup
        )
        self.history_button.grid(row=0, column=2, padx=10)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.reason_window_open = False

    def on_double_click(self, event):
        """
        Opens a tkinter messagebox with the reason.

        TODO: have a tk.toplevel here so that we can refocus if the window is already open.

        """
        if self.reason_window_open:
            return

        selection = self.tree.selection()[0]

        all_items = self.tree.get_children()
        selected_item_index = all_items.index(selection)

        item = self.data[selected_item_index]

        self.reason_window_open = True

        messagebox.showinfo(
            title=f"{item['Employee']}: Leave Request Reason",
            message=item["Reason"],
        )

        self.reason_window_open = False

    def open_history_popup(self):
        """
        Open the history popup displaying past vacation requests.
        """
        HistoryPopup(self, self.history)

    def get_selected_request(self):
        """
        Retrieve the selected vacation requests from the table.

        :return: List of selected indices if confirmed, otherwise None.
        """
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a request first.")
            return

        all_items = self.tree.get_children()
        selected_indices = [all_items.index(item) for item in selected_items]

        selected_data = [self.data[idx] for idx in selected_indices]
        confirmation_message = "\n".join(
            f"Employee: {item['Employee']}, Date: {item['From Date']} to {item['To Date']}, Reason: {item['Reason']}\n\n"
            for item in selected_data
        )

        confirm = messagebox.askyesno(
            "Confirm Selection",
            f"Are you sure you want to proceed?\n\n{confirmation_message}",
        )
        return selected_indices if confirm else None

    @gui_error_handler
    def approve_request(self):
        """
        Approve selected vacation requests and update the history.
        """
        selected_indices = self.get_selected_request()
        if selected_indices:
            to_approve_requests = [self.data[idx] for idx in selected_indices]

            for row in to_approve_requests:
                try:
                    mie_trak_funcs.approve_vacation_request(row.get("Vacation ID"))
                except Exception as e:
                    retry = messagebox.askretrycancel(
                        "Error while approving request", f"An error occurred: {e}"
                    )
                    if retry:
                        self.approve_request()
                    return

                row["Time Stamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                row["Status"] = "Approved"
                self.history.approved_requests.append(row)

            self.history.write_cache()
            self.refresh_data()

    @gui_error_handler
    def disapprove_request(self):
        """
        Disapprove selected vacation requests, notify the user, and update history.
        """
        selected_indices = self.get_selected_request()
        if selected_indices:
            to_disapprove_requests = [self.data[idx] for idx in selected_indices]

            for row in to_disapprove_requests:
                user_email = mie_trak_funcs.get_user_email_from_vacation_pk(
                    row["Vacation ID"]
                )
                user_body = simpledialog.askstring(
                    "Disapprove Request", "Add a note to send to the user"
                )
                if not user_body:
                    user_body = "No Note attached"
                    send = messagebox.askyesno(
                        "Confirm send email",
                        f"Confirm email to send.\nBody:\n {user_body}",
                    )
                    if send:
                        send_email(
                            to=user_email,
                            subject="Vacation Request Update",
                            body=user_body,
                        )

                row["Time Stamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                row["Status"] = "Disapproved"

                row["Note"] = f"{row['Time Stamp']}\n{user_body}"

                mie_trak_funcs.update_vacation_request_reason(
                    row.get("Vacation ID"), row.get("Note")
                )
                self.history.disapproved_requests.append(row)

            self.history.write_cache()
            self.refresh_data()

    @gui_error_handler
    def refresh_data(self):
        """
        Refresh the table data, removing disapproved requests from the view.
        """
        self.data = mie_trak_funcs.get_all_vacation_requests()
        self.tree.delete(*self.tree.get_children())

        disapproved_vacation_pks = [
            val.get("Vacation ID") for val in self.history.disapproved_requests
        ]
        new_data = []

        for row in self.data:
            if row["Vacation ID"] not in disapproved_vacation_pks:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["Vacation ID"],
                        row["Employee"],
                        row["From Date"],
                        row["To Date"],
                        row["Start Time"],
                        row["Hours"],
                        row["Reason"],
                        row["Approved"],
                    ),
                )
                new_data.append(row)

        self.data = new_data


class HistoryPopup(tk.Toplevel):
    """
    A popup window displaying past requests with filtering options.
    """

    def __init__(self, master, history):
        """
        Initialize the HistoryPopup window.

        :param master: The parent widget.
        :param history: An instance of RequestHistory containing past requests.
        """
        super().__init__(master)
        self.title("Past Requests")
        center_window(self, width=1000, height=500)

        self.history = history
        self.filter_var = tk.StringVar()

        self.build_widgets()
        self.update_table()

    def build_widgets(self):
        """
        Create and configure all widgets for the popup.
        """
        self.heading_label = ttk.Label(
            self, text="Past Requests", font=("Arial", 14, "bold")
        )
        self.heading_label.pack(pady=10)

        self.filter_combobox = ttk.Combobox(
            self,
            textvariable=self.filter_var,
            values=["All", "Approved", "Disapproved"],
        )
        self.filter_combobox.current(0)
        self.filter_combobox.pack(pady=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.update_table)

        columns = (
            "Vacation ID",
            "Employee",
            "From Date",
            "To Date",
            "Status",
            "Updated at",
            "Note",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.close_button.pack(pady=10)

    def update_table(self, event=None):
        """
        Update the table based on the selected filter option.

        :param event: The event triggering the update (optional).
        """
        selected_filter = self.filter_var.get()

        if selected_filter == "Approved":
            data = self.history.approved_requests
        elif selected_filter == "Disapproved":
            data = self.history.disapproved_requests
        else:
            data = self.history.approved_requests + self.history.disapproved_requests

        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert(
                "",
                "end",
                values=(  # to add default values maybe
                    row.get("Vacation ID", None),
                    row.get("Employee", None),
                    row.get("From Date", None),
                    row.get("To Date", None),
                    row.get("Status", None),
                    row.get("Time Stamp", None),
                    row.get("Note", None),
                ),
            )
