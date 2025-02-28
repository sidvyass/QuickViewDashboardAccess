import tkinter as tk
from tkinter import ttk
from typing import Dict
from gui.utils import gui_error_handler
from gui.vacation_request import center_window
from scripts import mie_trak_funcs


class AddView(tk.Toplevel):
    """
    Initializes the window for managing dashboards and quickviews.

    This constructor sets up the interface for assigning dashboards and quickviews to
    either a department or a user. It:

    - Initializes attributes related to the controller, callback function, and entity identifiers.
    - Configures the window appearance and dimensions.
    - Retrieves all available dashboards and quickviews from the system.
    - Removes dashboards and quickviews that have already been assigned to the selected
      department or user to prevent duplicate assignments.
    - Calls `build_widgets()` to construct the UI elements.

    Parameters:
        title (str): The title of the window.
        controller: The application controller handling business logic.
        call_back_update: A callback function to update data after modifications.
        department_pk (int | None, optional): The primary key of the selected department.
        user_pk (int | None, optional): The primary key of the selected user.
    """

    def __init__(
        self,
        title: str,
        controller,
        call_back_update,
        department_pk: int | None = None,
        user_pk: int | None = None,
    ) -> None:
        super().__init__()
        self.call_back_update = call_back_update
        self.controller = controller
        self.department_pk = department_pk
        self.user_pk = user_pk

        self._setup_window(title)
        self._initialize_data()
        self._remove_assigned_items()
        self.build_widgets()

    def _setup_window(self, title: str) -> None:
        """
        Configures the window settings, including size, title, and background.
        """
        self.title(title)
        center_window(self, width=500, height=500)
        self.configure(bg="#f4f4f4")  # Light gray background
        self.resizable(True, True)

    @gui_error_handler
    def _initialize_data(self) -> None:
        """
        Fetches all dashboards and quickviews from the system.
        """
        self.dashboards_dict = mie_trak_funcs.get_all_dashboards()
        self.quickviews_dict = mie_trak_funcs.get_all_quickviews()

    def _remove_assigned_items(self) -> None:
        """
        Removes dashboards and quickviews that are already assigned to the selected user or department.
        """
        if self.department_pk:
            self._remove_department_assigned_items()
        elif self.user_pk:
            self._remove_user_assigned_items()
        else:
            raise ValueError("Either department_pk or user_pk must be provided.")

    def _remove_department_assigned_items(self) -> None:
        """
        Removes dashboards and quickviews already assigned to the selected department.
        """
        department_data = self.controller.cache_dict.get(self.department_pk, {})
        accessed_dashboards = department_data.get("accessed_dashboards", {})
        accessed_quickviews = department_data.get("accessed_quickviews", {})

        for dashboard_pk in accessed_dashboards.keys():
            self.dashboards_dict.pop(dashboard_pk, None)

        for quickview_pk in accessed_quickviews.keys():
            self.quickviews_dict.pop(quickview_pk, None)

    @gui_error_handler
    def _remove_user_assigned_items(self) -> None:
        """
        Removes dashboards and quickviews already assigned to the selected user.
        """
        user_dashboards = mie_trak_funcs.get_user_dashboards(self.user_pk)
        user_quickviews = mie_trak_funcs.get_user_quick_view(self.user_pk)

        for dashboard_pk in user_dashboards.keys():
            self.dashboards_dict.pop(dashboard_pk, None)

        for quickview_pk in user_quickviews.keys():
            self.quickviews_dict.pop(quickview_pk, None)

    def build_widgets(self) -> None:
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

        self.dashboard_listbox = tk.Listbox(
            left_frame, selectmode=tk.MULTIPLE, exportselection=False, height=10
        )
        self.dashboard_listbox.pack(fill="both", expand=True)

        self.quickview_listbox = tk.Listbox(
            right_frame, selectmode=tk.MULTIPLE, exportselection=False, height=10
        )
        self.quickview_listbox.pack(fill="both", expand=True)

        self.populate_list(self.dashboard_listbox, self.dashboards_dict)
        self.populate_list(self.quickview_listbox, self.quickviews_dict)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="sew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        confirm_button = ttk.Button(
            button_frame, text="Confirm", command=self.confirm_selection
        )
        confirm_button.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

    def populate_list(self, listbox: tk.Listbox, data_dict: Dict[str, str]) -> None:
        """
        Populate a given listbox with items.
        """
        listbox.delete(0, tk.END)
        for _, description in data_dict.items():
            listbox.insert(tk.END, description)

    @gui_error_handler
    def confirm_selection(self) -> None:
        """
        Confirms the selection of dashboards and quickviews, assigning them to the selected user or department.

        This function:
        - Retrieves the selected dashboards and quickviews from the respective listboxes.
        - Assigns the selected dashboards and quickviews to either a department or a user based on the provided `department_pk` or `user_pk`.
        - Calls the appropriate functions to update the database or application state.
        - Triggers a UI update via `call_back_update` and closes the window.

        If neither `department_pk` nor `user_pk` is provided, the function does nothing.
        """

        selected_dashboard_indices = self.dashboard_listbox.curselection()
        selected_quickview_indices = self.quickview_listbox.curselection()

        selected_dashboards = [
            list(self.dashboards_dict.keys())[i] for i in selected_dashboard_indices
        ]
        selected_quickviews = [
            list(self.quickviews_dict.keys())[i] for i in selected_quickview_indices
        ]

        if self.department_pk:
            # Assign selected dashboards
            for dashboard_pk in selected_dashboards:
                self.controller.add_dashboard_to_department(
                    self.department_pk, dashboard_pk
                )

            # # Assign selected quickviews
            for quickview_pk in selected_quickviews:
                self.controller.add_quickview_to_department(
                    self.department_pk, quickview_pk
                )

        elif self.user_pk:
            print("executing user dashboard...")

            for dashboard_pk in selected_dashboards:
                mie_trak_funcs.add_dashboard_to_user(dashboard_pk, self.user_pk)

            for quickview_pk in selected_quickviews:
                mie_trak_funcs.add_quickview_to_user(quickview_pk, self.user_pk)

        self.call_back_update(event=None)  # Update main UI
        self.destroy()
