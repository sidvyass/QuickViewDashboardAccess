import tkinter as tk
from tkinter import ttk, messagebox
from pprint import pprint
from scripts import mie_trak_funcs


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

        # Insert data into the table
        for row in data:
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
            to_approve_requests_pks = [
                self.data[idx].get("Vacation ID") for idx in selected_indices
            ]

            for pk in to_approve_requests_pks:
                mie_trak_funcs.approve_vacation_request(pk)

        self.refresh_data()

    def disapprove_request(self):
        """Disapprove selected vacation request."""
        pass
        # selected = self.get_selected_request()
        # if selected:
        #     messagebox.showinfo("Disapproved", f"Vacation Request {selected[0]} disapproved.")

    def refresh_data(self):
        """Fetches and reloads the vacation requests data."""

        self.data = mie_trak_funcs.get_all_vacation_requests()
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
                    row["Start Time"],
                    row["Hours"],
                    row["Reason"],
                    row["Approved"],
                ),
            )
