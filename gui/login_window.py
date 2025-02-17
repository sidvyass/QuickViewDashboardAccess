import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from mt_api.connection import get_connection
from pprint import pprint


class LoginWindow(tk.Toplevel):
    def __init__(self, login_success_callback):
        super().__init__()

        self.login_success_callback = login_success_callback

        self.title("Login")
        self.geometry("350x200")
        self.resizable(False, False)

        # Configure grid layout
        self.columnconfigure(0, weight=1)  # Make single column expandable

        font_style = ("Arial", 12)

        # Username Label
        self.username_label = ttk.Label(self, text="Username:", font=font_style)
        self.username_label.grid(row=0, column=0, pady=(10, 2), padx=20, sticky="w")

        # Username Entry
        self.username_entry = ttk.Entry(self, font=font_style)
        self.username_entry.grid(row=1, column=0, pady=5, padx=20, sticky="ew")

        # Password Label
        self.password_label = ttk.Label(self, text="Password:", font=font_style)
        self.password_label.grid(row=2, column=0, pady=(10, 2), padx=20, sticky="w")

        # Password Entry
        self.password_entry = ttk.Entry(self, show="*", font=font_style)
        self.password_entry.grid(row=3, column=0, pady=5, padx=20, sticky="ew")

        # Login Button
        self.login_button = ttk.Button(self, text="Login", command=self.authenticate)
        self.login_button.grid(row=4, column=0, pady=15, padx=20, sticky="ew")

    def authenticate(self):
        """Handles authentication logic."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.verify_credentials(username, password):
            self.login_success_callback()
            self.destroy()  # Close login window
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def verify_credentials(self, username, password) -> bool:
        """Replace with real authentication logic (e.g., database check)."""

        query = "SELECT Code, Password FROM [User] WHERE Code = ?"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))

            results = cursor.fetchall()

            if len(results) > 1:
                messagebox.showwarning(title="Duplicates Found", message="The User table contains duplicate users with the same Code, please review")

            for _, mt_password in results:
                if password.casefold() == mt_password.casefold():
                    return True

        return False

