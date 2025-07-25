import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
#from LISmanager import LISmanager

CONFIG_FILE = "config.json"

class ConfigManager:
    
    def __init__(self):
        
        # Get the EFFScanner folder (parent of src)
        effscanner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parent_dir = os.path.dirname(effscanner_dir)
        
        # Default image path (inside EFFScanner/Data/img)
        self.default_image_path = os.path.join(parent_dir,"Data", "img", "JeldwenLogo.png")
    
        # Default JSON save path (inside EFFScanner/Data)
        self.json_save_path = os.path.join(parent_dir, "eff_saved_data.json")
    
        # Default LIS_Files folder (one step up from EFFScanner, in Data/LIS_Files)
        self.data_folder = os.path.join(parent_dir, "Data", "LIS_Files")

        self.load_config()
        
       

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.data_folder = config.get("data_folder", self.data_folder)
                self.json_save_path = config.get("json_save_path", self.json_save_path)
        else:
            self.save_config()  # Create config with defaults

    def save_config(self):
        config = {
            "data_folder": self.data_folder,
            "json_save_path": self.json_save_path
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def launch_gui(self):
        settings_window = tk.Toplevel()
        settings_window.title("Set Config Paths")
        settings_window.geometry("500x300")

        # GUI variables
        data_folder_var = tk.StringVar(value=self.data_folder)
        json_path_var = tk.StringVar(value=self.json_save_path)

        def choose_data_folder():
            path = filedialog.askdirectory(title="Select Data Folder (.lis files)")
            if path:
                data_folder_var.set(path)

        def choose_json_path():
            path = filedialog.asksaveasfilename(defaultextension=".json", title="Select Save Location for JSON File")
            if path:
                json_path_var.set(path)

        def save_and_exit():
            self.data_folder = data_folder_var.get()
            self.json_save_path = json_path_var.get()
            self.save_config()
            messagebox.showinfo("Saved", "Configuration saved successfully!")
            settings_window.destroy()

        # --- GUI Layout ---
        tk.Label(settings_window, text="Data Folder (.lis):").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(settings_window, textvariable=data_folder_var, width=60).pack(padx=10)
        tk.Button(settings_window, text="Browse", command=choose_data_folder).pack(pady=5)

        tk.Label(settings_window, text="JSON Save Path:").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Entry(settings_window, textvariable=json_path_var, width=60).pack(padx=10)
        tk.Button(settings_window, text="Browse", command=choose_json_path).pack(pady=5)

        tk.Button(settings_window, text="Save & Exit", command=save_and_exit).pack(pady=20)

        settings_window.mainloop()