import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk, messagebox
from datetime import datetime
from scripts import mie_trak_funcs
from scripts.controller import send_email
from scripts.request_history import RequestHistory
from base_logger import getlogger


LOGGER = getlogger("VR Window")


def center_window(window, width=1000, height=700):
    """Centers a Tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")


class VacationRequestsWindow(tk.Toplevel):
    def __init__(self, master, data):
        super().__init__(master)
        self.title("Vacation Requests")
        center_window(self, width=1500)

        self.data = data

        # Heading
        self.heading_label = ttk.Label(
            self, text="Vacation Requests", font=("Arial", 14, "bold")
        )
        self.heading_label.pack(pady=10)

        # Table (Treeview)
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

        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons Frame
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

        self.history = RequestHistory()

        self.refresh_data()

    def open_history_popup(self):
        """Opens the history popup window."""
        HistoryPopup(self, self.history)

    def get_selected_request(self):
        """Retrieve selected row data from the table."""
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

    def approve_request(self):
        """Approve selected vacation request."""
        selected_indices = self.get_selected_request()

        if selected_indices:
            to_approve_requests = [self.data[idx] for idx in selected_indices]

            for row in to_approve_requests:
                # can we be sure that this exists?
                mie_trak_funcs.approve_vacation_request(row.get("Vacation ID"))
                row["Time Stamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                row["Status"] = "Approved"
                self.history.approved_requests.append(row)

            self.history.write_cache()

            self.refresh_data()

    def disapprove_request(self):
        """Disapprove selected vacation request."""
        selected_indices = self.get_selected_request()

        if selected_indices:
            to_disapprove_requests = [self.data[idx] for idx in selected_indices]

            for row in to_disapprove_requests:
                # block to get the user and send email
                user_email = mie_trak_funcs.get_user_email_from_vacation_pk(
                    row["Vacation ID"]
                )
                user_body = simpledialog.askstring(
                    title="Disapprove Request", prompt="Add a note to send to the user"
                )
                if not user_body:
                    user_body = "No Note attached"

                send_email(to=user_email, subject="test", body=user_body)
                # -----------------------

                row["Time Stamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                row["Status"] = "Disapproved"
                self.history.disapproved_requests.append(row)

            self.history.write_cache()

            self.refresh_data()

    def refresh_data(self):
        """Fetches and reloads the vacation requests data."""

        self.data = mie_trak_funcs.get_all_vacation_requests()
        self.tree.delete(*self.tree.get_children())

        # NOTE: Our SQL query does not pull approved requests.
        # When the user disapproves requests, the request needs to be removed from view
        # the following code removes all the disapproved requests by checking the PK.

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

        # Since we are using this to get our selection, we update it everytime we refresh.
        self.data = new_data  # NOTE: this is used in the select function.


class HistoryPopup(tk.Toplevel):
    def __init__(self, master, history: RequestHistory):
        super().__init__(master)
        self.title("Past Requests")
        center_window(self, width=800, height=500)

        self.heading_label = ttk.Label(
            self, text="Past Requests", font=("Arial", 14, "bold")
        )
        self.heading_label.pack(pady=10)

        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(
            self,
            textvariable=self.filter_var,
            values=["All", "Approved", "Disapproved"],
        )
        self.filter_combobox.current(0)  # Default to "All"
        self.filter_combobox.pack(pady=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.update_table)

        columns = (
            "Vacation ID",
            "Employee",
            "From Date",
            "To Date",
            "Status",
            "Updated at",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Close Button
        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.close_button.pack(pady=10)

        self.history = history

        self.update_table()

    def update_table(self, event=None):
        """Updates the table based on the filter selection."""
        selected_filter = self.filter_var.get()

        if selected_filter == "Approved":
            self.data = self.history.approved_requests

        elif selected_filter == "Disapproved":
            self.data = self.history.disapproved_requests

        else:
            self.data = (
                self.history.approved_requests + self.history.disapproved_requests
            )

        self.tree.delete(*self.tree.get_children())

        for row in self.data:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["Vacation ID"],
                    row["Employee"],
                    row["From Date"],
                    row["To Date"],
                    row["Status"],
                    row["Time Stamp"],
                ),
            )
