import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from scripts import mie_trak_funcs
from base_logger import getlogger

LOGGER = getlogger("Login")


class LoginWindow(tk.Toplevel):
    def __init__(self, login_success_callback):
        super().__init__()
        self.login_success_callback = login_success_callback

        self.title("Login")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")  # Light gray background
        self.columnconfigure(0, weight=1)  # Centering the frame

        heading_font = ("Arial", 16, "bold")
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        frame.columnconfigure(0, weight=1)

        self.heading_label = ttk.Label(
            frame, text="Login", font=heading_font, anchor="center"
        )
        self.heading_label.grid(row=0, column=0, pady=(5, 15), sticky="ew")

        self.username_label = ttk.Label(frame, text="Username:", font=label_font)
        self.username_label.grid(row=1, column=0, sticky="w", pady=(5, 2))

        self.username_entry = ttk.Entry(frame, font=entry_font)
        self.username_entry.grid(row=2, column=0, sticky="ew", pady=5)

        self.password_label = ttk.Label(frame, text="Password:", font=label_font)
        self.password_label.grid(row=3, column=0, sticky="w", pady=(5, 2))

        self.password_entry = ttk.Entry(frame, show="*", font=entry_font)
        self.password_entry.grid(row=4, column=0, sticky="ew", pady=5)

        self.login_button = ttk.Button(frame, text="Login", command=self.authenticate)
        self.login_button.grid(row=5, column=0, sticky="ew", pady=15)

    def authenticate(self):
        """Handles authentication logic."""
        self.login_success_callback()
        self.destroy()
        # username = self.username_entry.get()
        # password = self.password_entry.get()
        #
        # if mie_trak_funcs.login_user(username, password):
        #     self.login_success_callback()
        #     LOGGER.info(f"User: {username} logged in.")
        #     self.destroy()
        # else:
        #     messagebox.showerror("Login Failed", "Invalid username or password.")
