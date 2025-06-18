import tkinter as tk
from tkinter import ttk
from dataManager import DataManager
from effscanner import EFFScanner


class EffDataTableGUI:
    def __init__(self, root, startup_frame):
        self.root = root
        self.startup_frame = startup_frame
        self.filter_on = False
        self.data_manager = DataManager()
        self.data_frame = None
        
        
    
    def toggle_filter(self, tree, filter_btn):
        self.filter_on = not self.filter_on
        filter_btn.config(text=f"Filter Images: {'ON' if self.filter_on else 'OFF'}")
        self.populate_tree(tree)
    
    
    def back_to_menu(self, frame):
        frame.pack_forget()
        self.startup_frame.pack(padx=20, pady=20)   
    
    
    def populate_tree(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        data = self.data_manager.get_all()
        items = data.items()
        if self.filter_on:
            items = filter(lambda kv: kv[1] > 0, items)
        for idx, (key, value) in enumerate(items):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tree.insert("", "end", values=(key, value), tags=(tag,))   
     
     
        
    def show_data_ui(self):
        self.startup_frame.pack_forget()
        if self.data_frame:
            self.data_frame.destroy()
        self.data_frame = tk.Frame(self.root, bg="#1d446b")
        self.data_frame.pack(padx=20, pady=20, fill="both", expand=True)

        header_frame = tk.Frame(self.data_frame, bg="#1d446b")
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="EFF Scanned Data:", bg="#1d446b", fg="white", font=("Arial", 14)).pack(side="left", padx=10, pady=10)
        tk.Button(header_frame, text="Back to the main menu", command=lambda: self.back_to_menu(self.data_frame)).pack(side="right", padx=10, pady=10)
        filter_btn = tk.Button(header_frame, text="Filter Images: OFF", command=lambda: self.toggle_filter(tree, filter_btn))
        filter_btn.pack(side="right", padx=10, pady=10)

        tree_frame = tk.Frame(self.data_frame)
        tree_frame.pack(pady=5, fill="both", expand=True)

        y_scroll = tk.Scrollbar(tree_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")
        x_scroll = tk.Scrollbar(tree_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        tree = ttk.Treeview(tree_frame, columns=("Key", "Value"), show="headings",
                            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set, height=20)
        tree.heading("Key", text="Key")
        tree.heading("Value", text="Value")
        tree.column("Key", width=120, anchor="center")
        tree.column("Value", width=80, anchor="center")
        tree.pack(fill="both", expand=True)

        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)

        self.populate_tree(tree)

        tree.tag_configure("evenrow", background="#e0e0e0")
        tree.tag_configure("oddrow", background="#f5f5f5")
