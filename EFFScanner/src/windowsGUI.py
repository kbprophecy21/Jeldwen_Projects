import tkinter as tk
from tkinter import messagebox, PhotoImage
from tkinter import ttk
from dataManager import DataManager
from effscanner import EFFScanner
from ScannedTicketTable import ScannedTicketTable
from effDataTableGUI import EffDataTableGUI
from config_manager import ConfigManager
from datetime import datetime


class EFFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeldwen EFF Scanner")
        self.root.configure(bg="#00406b")
        
        self.config = ConfigManager()

        # Jeldwen Logo -----------------------------------# 
        self.logo_img = PhotoImage(file=self.config.image_path)  # Load the logo image from the config path
        logo_label = tk.Label(self.root, image=self.logo_img, bg="#f5f5f5")
        logo_label.pack(pady=10)
        #--------------------------------------------------#
        
        # Create the main startup frame 
        self.startup_frame = tk.Frame(self.root, bg="#1d446b")
        self.startup_frame.pack(padx=20, pady=20)
        #---------------------------------------------------#
        
        # Create the Menu Bar on the top left corner of the window
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Reset EFF Data", command=self.reset_eff_data)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        # Help Menu -----------------------------------#
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: tk.messagebox.showinfo("About", "Jeldwen EFF Scanner GUI v1.0\n by Kyle Brewer \nSoftware Engineer"))
        help_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)
        #--------------------------------------------------#

        self.data_manager = DataManager() # Initialize the DataManager so it can be used throughout the app

        self.scanned_tickets = [] 
        self.effDataTable = EffDataTableGUI(self.root, self.startup_frame) # Initialize the EffDataTableGUI for displaying EFF data
        
        self.scannedTicketTable = ScannedTicketTable(
        self.root,
        self.startup_frame,
        self.scanned_tickets,
        on_update_callback=lambda ticket: self.effDataTable.populate_tree(self.effDataTable.tree),
        on_delete_callback=lambda idx: self.effDataTable.populate_tree(self.effDataTable.tree)
        )
         
        self.table_page = None
        self.ticket_table = None

        # Main menu UI Buttons ---------------------------------------------------#
        tk.Label(self.startup_frame, text="Choose an option on the menu:", font=("Arial", 14), bg="#1d446b", fg="white").pack(pady=10)
        tk.Button(self.startup_frame, text="Scan Ticket", width=25, command=self.show_scan_ui).pack(pady=5)
        tk.Button(self.startup_frame, text="See EFF's Scanned Data", width=25, command=self.effDataTable.show_data_ui).pack(pady=5)
        tk.Button(self.startup_frame, text="Prev-Scanned Tickets", width=25, command=self.scannedTicketTable.show_scanned_tickets_ui).pack(pady=5)
        #--------------------------------------------------#
        
        self.scan_frame = None
        self.data_frame = None
        
        
    def open_settings(self):
        config = ConfigManager()
        config.launch_gui()

    def show_scan_ui(self):
        self.startup_frame.pack_forget()
        if self.scan_frame:
            self.scan_frame.destroy()
        self.scan_frame = tk.Frame(self.root, bg="#1d446b")
        self.scan_frame.pack(padx=20, pady=20)

        tk.Label(self.scan_frame, text="Scan or Enter Schedule Batch:", bg="#1d446b", fg="white").pack(pady=10)
        self.entry = tk.Entry(self.scan_frame, width=40)
        self.entry.pack(pady=5)
        self.entry.focus()
        self.entry.bind("<Return>", lambda event: self.scan_ticket())

        tk.Button(self.scan_frame, text="Submit", command=self.scan_ticket).pack(pady=5)
        tk.Button(self.scan_frame, text="Back to the main menu", command=lambda: self.back_to_menu(self.scan_frame)).pack(pady=10)
        self.status = tk.Label(self.scan_frame, text="", fg="yellow", bg="#1d446b")
        self.status.pack(pady=5)

        total = self.data_manager.get_total()
        self.total_label = tk.Label(self.scan_frame, text=f"Total: {total}", bg="#1d446b", fg="yellow", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=(10, 0))

    

    def scan_ticket(self):
        batch_id = self.entry.get().strip()
        if not batch_id:
            self.status.config(text="Please enter a schedule batch.", fg="red")
            return

        folder_path = self.config.data_folder
        if not folder_path:
            messagebox.showerror("Error", "Data folder path is not set. Please configure it in the settings.")
            return

        scanner = EFFScanner(folder_path, batch_id)
        scanner.find_ticket()

        extended_df = scanner.get_extended_data()
        if not extended_df.empty:
            updated_keys = []
            for _, row in extended_df.iterrows():
                try:
                    quantity = int(row["quantity"])
                except Exception:
                    quantity = 1

                frame_code = row["frame_code"]
                door_size = row["door_size"]

                ticket = row.to_dict()
                ticket["batch_id"] = batch_id
                ticket["quantity"] = quantity
                ticket["scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.data_manager.add_ticket(ticket)      # save full data + categorize
                self.scanned_tickets.append(ticket)       # used by the table GUI

                key = self.data_manager.categorize_ticket(frame_code, door_size, quantity)
                if key:
                    updated_keys.append(f"{key} (+{quantity})")

            keys_str = ", ".join(updated_keys)
            self.status.config(text=f"✅ Ticket(s) processed.\nUpdated: {keys_str}", fg="green")
        else:
            self.status.config(text="❌ Ticket not found.", fg="red")

        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.total_label.config(text=f"Total Doors: {self.data_manager.get_total()}")


  
    def reset_eff_data(self):
        self.data_manager.reset_data()
        if hasattr(self, "total_label"):
            self.total_label.config(text=f"Total Doors: {self.data_manager.get_total()}")

    def back_to_menu(self, frame_to_destroy=None):
        if frame_to_destroy:
            frame_to_destroy.destroy()
        self.startup_frame.pack(padx=20, pady=20)

        
    def run_app(self):
        self.root.mainloop()
