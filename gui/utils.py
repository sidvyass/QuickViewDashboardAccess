import functools
from tkinter import messagebox


def gui_error_handler(func):
    """
    A decorator to handle database-related errors in Tkinter GUI functions.

    This decorator catches database-related exceptions and displays an appropriate
    message box for the user, allowing them to retry or cancel the operation.

    Does not log any errors, only catches errors by the pyodbc wrapper defined in mie_trak_funcs.py.

    :type logger: logging.Logger or None
    :return: A wrapped function with error handling.
    :rtype: Callable
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except RuntimeError as e:  # Catching RuntimeError from `with_db_conn`
                retry = messagebox.askretrycancel(
                    title="Database Error",
                    message=f"{e}\n\nWould you like to retry?",
                )
                if not retry:
                    return None  # Exit function on cancel
            except Exception as e:
                messagebox.showerror(
                    title="Unexpected Error",
                    message=f"An unexpected error occurred:\n\n{e}",
                )
                return None  # Exit function

    return wrapper


def center_window(window, width=1000, height=700):
    """Centers a Tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")
