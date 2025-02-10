import tkinter as tk
from tkinter import ttk
from mie_trak import MieTrak


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
        self.combo2.bind("<<ComboboxSelected>>", self.update_with_dashboards_or_quickview)

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

        self.mie_trak = MieTrak()

    def update_with_users_or_department(self, event):
        self.user_department_listbox.delete(0, tk.END)
        selection = self.combo1.get()

        if selection == "User":
            self.user_data = self.mie_trak.get_user_data()
            for userpk, user_info in self.user_data.items():
                self.user_department_listbox.insert(tk.END, f"{user_info[0]} {user_info[1]}")
        elif selection == "Department":
            self.department_data = self.mie_trak.get_department()
            for departmentpk, name in self.department_data.items():
                self.user_department_listbox.insert(tk.END, f"{name}")

    def show_accessed_dashboards_quickview(self, event):
        self.listbox2.delete(0, tk.END)
        user_or_department = "User" if self.combo1.get() == "User" else "Department"
        selection = self.user_department_listbox.curselection()

        if not selection:
            return

        def find_user_pk_from_selection(index_to_find):
            i = 0
            for userpk, values in self.user_data.items():
                if i == index_to_find:
                    return userpk
                i += 1

        if user_or_department == "User":
            userpk = find_user_pk_from_selection(selection[0])
            data = self.mie_trak.get_user_dashboards(userpk) if self.combo2.get() == "Dashboards" else self.mie_trak.get_user_quick_view(userpk)
            for pk, name in data.items():
                self.listbox2.insert(tk.END, name)

    def update_with_dashboards_or_quickview(self, event):
        selection = self.combo2.get()
        self.listbox2.delete(0, tk.END)
        self.listbox2.insert(tk.END, f"Items for {selection}")

    def add_item(self):
        # here we pop open a new window with a listbox and the dashboards. 



        self.user_department_listbox.insert(tk.END, "New Item 1")
        self.listbox2.insert(tk.END, "New Item 2")

    def delete_item(self):
        if self.user_department_listbox.curselection():
            self.user_department_listbox.delete(self.user_department_listbox.curselection())
        if self.listbox2.curselection():
            self.listbox2.delete(self.listbox2.curselection())

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTkinterGUI(root)
    root.mainloop()

