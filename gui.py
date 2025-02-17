import tkinter as tk
from tkinter import ttk
from typing import Dict
from controller import Controller
from scripts.add_popup import AddView
from scripts import mie_trak_funcs
from tkinter import messagebox
from pprint import pprint


class SimpleTkinterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Tkinter GUI")
        self.root.configure(bg="#f4f4f4")  # Light grey background
        self.root.geometry("600x500")  # Increased window size

        # Configure grid layout to be flexible
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Define styles
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
        style.configure("TLabel", background="#f4f4f4", font=("Arial", 12))
        style.configure("TCombobox", padding=5)

        # Main Frame
        frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20, relief="ridge", bd=2)
        frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)

        # Heading
        self.heading = tk.Label(frame, text="Doc Control", font=("Arial", 16, "bold"), bg="#ffffff")
        self.heading.pack(pady=10)

        # Subframes for alignment
        self.subframe1 = tk.Frame(root, bg="#f4f4f4")
        self.subframe1.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.subframe1.columnconfigure(0, weight=1)
        self.subframe1.rowconfigure(1, weight=1)

        self.subframe2 = tk.Frame(root, bg="#f4f4f4")
        self.subframe2.grid(row=1, column=1, padx=15, pady=5, sticky="nsew")
        self.subframe2.columnconfigure(0, weight=1)
        self.subframe2.rowconfigure(1, weight=1)

        # Subheadings
        self.users_label = ttk.Label(self.subframe1, text="Users", font=("Arial", 12, "bold"))
        self.users_label.pack()

        self.dashboards_label = ttk.Label(self.subframe2, text="Accessed Dashboards", font=("Arial", 12, "bold"))
        self.dashboards_label.pack()

        # Comboboxes
        self.combo1 = ttk.Combobox(self.subframe1, values=["User", "Department"], state="readonly")
        self.combo1.pack(pady=5)
        self.combo1.bind("<<ComboboxSelected>>", self.update_with_users_or_department)

        self.combo2 = ttk.Combobox(self.subframe2, values=["Dashboards", "QuickViews"], state="readonly")
        self.combo2.pack(pady=5)
        self.combo2.bind("<<ComboboxSelected>>", self.show_accessed_dashboards_quickview)
        self.combo2.set("Dashboards")

        # Listboxes
        self.user_department_listbox = tk.Listbox(self.subframe1, exportselection=False, relief="solid", bd=1)
        self.user_department_listbox.pack(pady=5, fill="both", expand=True)
        self.user_department_listbox.bind("<<ListboxSelect>>", self.show_accessed_dashboards_quickview)

        self.listbox2 = tk.Listbox(self.subframe2, relief="solid", bd=1)
        self.listbox2.pack(pady=5, fill="both", expand=True)

        # Buttons
        self.button_frame = tk.Frame(root, bg="#f4f4f4")
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")

        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_item)
        self.add_button.grid(row=0, column=0, padx=10)

        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_item)
        self.delete_button.grid(row=0, column=1, padx=10)

        self.controller = Controller()

    def update_with_users_or_department(self, event):
        self.user_department_listbox.delete(0, tk.END)
        selection = self.combo1.get()

        if selection == "User":
            self.user_data = mie_trak_funcs.get_user_data(enabled=True)
            for _, user_info in self.user_data.items():
                self.user_department_listbox.insert(tk.END, f"{user_info[0]} {user_info[1]}")
        elif selection == "Department":
            self.department_data = mie_trak_funcs.get_all_departments()
            for _, name in self.department_data.items():
                self.user_department_listbox.insert(tk.END, f"{name}")

    def show_accessed_dashboards_quickview(self, event):
        self.listbox2.delete(0, tk.END)

        selection = self.user_department_listbox.curselection()
        if not selection:
            messagebox.showerror(title="Selection Invalid", message="Please select a User/Department from the list to view accessed itmes")
            return

        db_or_qv: str = self.combo2.get()
        user_or_department = "User" if self.combo1.get() == "User" else "Department"

        if user_or_department == "User":
            userpk = list(self.user_data.keys())[selection[0]]
            data_to_display = mie_trak_funcs.get_user_dashboards(userpk) if db_or_qv == "Dashboards" else mie_trak_funcs.get_user_quick_view(userpk)

        elif user_or_department == "Department":
            department_data: Dict = self.controller.get_department_information_from_cache()
            selected_department_pk = list(department_data.keys())[selection[0]]

            accessed_key = "accessed_dashboards" if db_or_qv == "Dashboards" else "accessed_quickviews"
            data_to_display = department_data.get(selected_department_pk, {}).get(accessed_key, {})

        else:
            # message: invalid department
            data_to_display = {}

        if data_to_display:
            for _, name in data_to_display.items():
                self.listbox2.insert(tk.END, name)
        else:
            self.listbox2.insert(tk.END, "N/A")


    def add_item(self):
        # LIVE: 
        user_or_department_type = self.combo1.get()
        department_or_user_selection_index = self.user_department_listbox.curselection()[0]

        if not user_or_department_type or not department_or_user_selection_index:
            messagebox.showerror(title="Selection Error", message="Please select User/Department first and then make a selection from the list before clicking add.")
            return

        department_data_dict = self.controller.get_department_information_from_cache()

        if user_or_department_type == "User":
            user_pk = list(self.user_data.keys())[department_or_user_selection_index]
            AddView("User", self.controller, self.show_accessed_dashboards_quickview, user_pk=user_pk)

        elif user_or_department_type == "Department":
            department_pk = list(department_data_dict.keys())[department_or_user_selection_index]
            department_name = department_data_dict.get(department_pk, {}).get("name", {})

            if not department_name:
                messagebox.showerror(title="Department Name Error", message="Department Name could not be resolved, contact developer.")
                return

            AddView(department_name, self.controller, self.show_accessed_dashboards_quickview, department_pk=department_pk)

        else:
            # display error to the user
            pass


    def delete_item(self):
        if self.user_department_listbox.curselection():
            self.user_department_listbox.delete(self.user_department_listbox.curselection())
        if self.listbox2.curselection():
            self.listbox2.delete(self.listbox2.curselection())

        # TODO: Delete from database


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTkinterGUI(root)
    root.mainloop()


