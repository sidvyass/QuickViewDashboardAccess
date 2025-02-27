import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from mt_api.connection import get_connection


class LoginWindow(tk.Toplevel):
    def __init__(self, login_success_callback):
        super().__init__()

        self.login_success_callback = login_success_callback

        self.title("Login")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")  # Light gray background for a modern UI

        # Configure main grid layout
        self.columnconfigure(0, weight=1)  # Centering the frame

        # Modern font styles
        heading_font = ("Arial", 16, "bold")
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        # Frame for better layout and padding
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid inside the frame
        frame.columnconfigure(0, weight=1)  # Expands all elements in the column

        # Login Heading
        self.heading_label = ttk.Label(
            frame, text="Login", font=heading_font, anchor="center"
        )
        self.heading_label.grid(row=0, column=0, pady=(5, 15), sticky="ew")

        # Username Label
        self.username_label = ttk.Label(frame, text="Username:", font=label_font)
        self.username_label.grid(row=1, column=0, sticky="w", pady=(5, 2))

        # Username Entry
        self.username_entry = ttk.Entry(frame, font=entry_font)
        self.username_entry.grid(row=2, column=0, sticky="ew", pady=5)

        # Password Label
        self.password_label = ttk.Label(frame, text="Password:", font=label_font)
        self.password_label.grid(row=3, column=0, sticky="w", pady=(5, 2))

        # Password Entry
        self.password_entry = ttk.Entry(frame, show="*", font=entry_font)
        self.password_entry.grid(row=4, column=0, sticky="ew", pady=5)

        # Login Button
        self.login_button = ttk.Button(frame, text="Login", command=self.authenticate)
        self.login_button.grid(row=5, column=0, sticky="ew", pady=15)

    def authenticate(self):
        """Handles authentication logic."""
        # DEBUG:
        self.login_success_callback()
        self.destroy()

        # LIVE:
        # username = self.username_entry.get()
        # password = self.password_entry.get()
        #
        # if self.verify_credentials(username, password):
        #     self.login_success_callback()
        #     self.destroy()  # Close login window
        # else:
        #     messagebox.showerror("Login Failed", "Invalid username or password.")

    def verify_credentials(self, username, password) -> bool:
        """Replace with real authentication logic (e.g., database check)."""

        query = "SELECT Code, Password FROM [User] WHERE Code = ?"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            results = cursor.fetchall()

            if len(results) > 1:
                messagebox.showwarning(
                    title="Duplicates Found",
                    message="The User table contains duplicate users with the same Code, please review",
                )

            for _, mt_password in results:
                if password.casefold() == mt_password.casefold():
                    return True

        return False
