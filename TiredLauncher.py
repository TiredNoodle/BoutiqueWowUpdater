import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import subprocess
import configparser
import webbrowser

class RealmlistWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Set Realmlist")
        self.geometry("300x160")  # Set window size to 300x160

        self.callback = callback

        # Realmlist Entry
        tk.Label(self, text="Realmlist URL:").pack(pady=5)
        self.realmlist_entry = tk.Entry(self, width=30)
        self.realmlist_entry.pack(pady=5)

        # Set Button
        set_button = tk.Button(self, text="Set", command=self.set_realmlist)
        set_button.pack(pady=10, side=tk.RIGHT)

        # Bind ENTER key to the Set button
        self.bind("<Return>", lambda event: set_button.invoke())

    def set_realmlist(self):
        realmlist_url = self.realmlist_entry.get()
        success = self.callback(realmlist_url)
        if success:
            messagebox.showinfo("Success", "Realmlist set to: {}".format(realmlist_url))
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to set realmlist URL.")

class ManageRealmsWindow(tk.Toplevel):
    def __init__(self, parent, launcher):
        super().__init__(parent)
        self.title("Manage Realms")
        self.geometry("420x240")  # Set window size to 420x240 (40 units taller)

        self.launcher = launcher

        # Listbox to display realms
        self.realms_listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.realms_listbox.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Frame to contain buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=10, padx=10)

        # Buttons to add and remove realms
        add_button = tk.Button(button_frame, text="+ Add", command=self.add_realm)
        add_button.pack(side=tk.LEFT, padx=10, pady=5)
        set_button = tk.Button(button_frame, text="Set", command=self.set_realm)
        set_button.pack(side=tk.LEFT, padx=10, pady=5)
        remove_button = tk.Button(button_frame, text="- Remove", command=self.remove_realm)
        remove_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Load realms from config
        self.load_realms_from_config()

    def add_realm(self):
        realm_name = simpledialog.askstring("Add Realm", "Enter Realm Name:", parent=self)
        if realm_name:
            self.realms_listbox.insert(tk.END, realm_name)
            self.save_realms_to_config()

    def set_realm(self):
        selected_index = self.realms_listbox.curselection()
        if selected_index:
            realm_name = self.realms_listbox.get(selected_index)
            self.launcher.set_realmlist_callback(realm_name)

    def remove_realm(self):
        selected_index = self.realms_listbox.curselection()
        if selected_index:
            self.realms_listbox.delete(selected_index)
            self.save_realms_to_config()

    def load_realms_from_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        realms = config.get('Realms', 'realm_list', fallback='').split(',')
        for realm in realms:
            if realm:
                self.realms_listbox.insert(tk.END, realm)

    def save_realms_to_config(self):
        config = configparser.ConfigParser()

        # Preserve existing values
        config.read('config.ini')
        wow_directory = config.get('Config', 'wow_directory', fallback='')
        realmlist_url = config.get('Config', 'realmlist_url', fallback='')

        realms = [self.realms_listbox.get(idx) for idx in range(self.realms_listbox.size())]
        config['Realms'] = {'realm_list': ','.join(realms)}

        # Add preserved values to the configuration
        config['Config'] = {'wow_directory': wow_directory,
                            'realmlist_url': realmlist_url}

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

class TiredLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Tired Launcher")
        self.root.geometry("640x480")

        # Variables for configuration
        self.wow_directory = tk.StringVar()
        self.realmlist_url = tk.StringVar()

        # GUI components
        self.create_widgets()

        # Load configuration
        self.load_config()

    def create_widgets(self):
        # Menu Bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Options Menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Set Path to WoW Executable", command=self.browse_wow_directory)

        # Realms Menu
        realms_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Realms", menu=realms_menu)
        realms_menu.add_command(label="Set Active", command=self.set_active_realm)
        realms_menu.add_command(label="Manage", command=self.manage_realms)

        # Updates Menu
        updates_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Updates", menu=updates_menu)
        updates_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        updates_menu.add_command(label="Source", command=self.open_source)

        # WoW Directory Entry
        tk.Label(self.root, text="WoW Directory:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        entry_wow_directory = tk.Entry(self.root, textvariable=self.wow_directory, width=30)
        entry_wow_directory.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        # Launch Button
        tk.Button(self.root, text="Launch WoW", command=self.launch_wow).grid(row=2, column=2, pady=10, padx=(0, 10), sticky='ew')

        # Configure row and column weights to make the Launch WoW button expand
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def browse_wow_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.wow_directory.set(directory)
            self.save_config()

    def launch_wow(self):
        wow_executable_path = os.path.join(self.wow_directory.get(), "Wow.exe")
        if os.path.isfile(wow_executable_path):
            subprocess.Popen([wow_executable_path])
        else:
            messagebox.showerror("Error", "Wow.exe not found. Please set the correct path to the WoW executable.")

    def manage_realms(self):
        realms_window = ManageRealmsWindow(self.root, self)

    def set_active_realm(self):
        realmlist_window = RealmlistWindow(self.root, self.set_realmlist_callback)

    def set_realmlist_callback(self, realmlist_url):
        if realmlist_url:
            wow_folder = self.wow_directory.get()
            realmlist_path = os.path.join(wow_folder, "Data", "enUS", "realmlist.wtf")

            try:
                with open(realmlist_path, "w") as realmlist_file:
                    realmlist_file.write(f"set realmlist \"{realmlist_url}\"")
                print(f"Realmlist set successfully to: {realmlist_url}")
                return True
            except Exception as e:
                print(f"Error setting realmlist: {e}")
                messagebox.showerror("Error", f"Failed to set realmlist URL: {e}")
                return False
        else:
            print("Realmlist URL is empty.")
            messagebox.showerror("Error", "Realmlist URL cannot be empty.")
            return False

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.wow_directory.set(config.get('Config', 'wow_directory', fallback=''))
        self.realmlist_url.set(config.get('Config', 'realmlist_url', fallback=''))

    def save_config(self):
        config = configparser.ConfigParser()

        # Preserve existing values
        config.read('config.ini')
        realmlist_url = config.get('Config', 'realmlist_url', fallback='')

        # Add preserved values to the configuration
        config['Config'] = {'wow_directory': self.wow_directory.get(),
                            'realmlist_url': realmlist_url}

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    def check_for_updates(self):
        # Simulate checking for updates
        messagebox.showinfo("Updates", "No updates available at the moment.")

    def open_source(self):
        # Open the source code in the default web browser
        webbrowser.open("https://github.com/TiredNoodle/BoutiqueWowUpdater")

if __name__ == "__main__":
    root = tk.Tk()
    launcher = TiredLauncher(root)
    root.mainloop()
