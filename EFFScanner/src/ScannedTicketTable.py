import tkinter as tk
from tkinter import ttk, messagebox
from dataManager import DataManager

class ScannedTicketTable:
    def __init__(self, root, startup_frame, data_manager, on_update_callback=None, on_delete_callback=None):
        self.root = root
        self.startup_frame = startup_frame
        self.data_manager = data_manager  # shared instance of DataManager in other classes
        self.scanned_tickets = self.data_manager.get_ticket_history()
        self.on_update_callback = on_update_callback
        self.on_delete_callback = on_delete_callback
        self.frame = None  
        self.tree = None
        self.sort_recent_first = False  # Add this line

    def refresh_table(self):
        if self.sort_recent_first:
            self.scanned_tickets = list(reversed(self.scanned_tickets))

        if not self.tree:
            return 
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for idx, ticket in enumerate(self.scanned_tickets):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", iid=str(idx), values=(
                ticket.get("batch_id", ""),
                ticket.get("sequence_number", ""),
                ticket.get("order_number", ""),
                ticket.get("item_number", ""),
                ticket.get("door_species", ""),
                ticket.get("quantity", ""),
                ticket.get("customer", ""),
                ticket.get("scan_time", "")
            ), tags=(tag,))

        self.tree.tag_configure("evenrow", background="#e0e0e0")
        self.tree.tag_configure("oddrow", background="#f5f5f5")

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        col_index = int(column.replace("#", "")) - 1
        col_name = self.tree["columns"][col_index]
        if col_name != "quantity":
            return

        x, y, width, height = self.tree.bbox(row_id, column)
        value = self.tree.set(row_id, column)

        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            try:
                new_quantity = int(entry.get())
                idx = int(row_id)
                original_ticket = self.scanned_tickets[idx]

                if new_quantity == original_ticket.get("quantity"):
                    return

                updated_ticket = original_ticket.copy()
                updated_ticket["quantity"] = new_quantity

                self.data_manager.reprocess_ticket(original_ticket, updated_ticket)
                self.refresh_table()

                if self.on_update_callback:
                    self.on_update_callback(updated_ticket)

            except ValueError:
                messagebox.showerror("Invalid Input", "Quantity must be a number.")
            finally:
                entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def delete_selected_ticket(self):
        selected_item = self.tree.selection()
        if selected_item:
            idx = int(selected_item[0])
            ticket = self.scanned_tickets[idx]

            self.data_manager.delete_ticket_by_data(ticket)
            self.refresh_table()

            if self.on_delete_callback:
                self.on_delete_callback(ticket)
        else:
            messagebox.showinfo("No selection", "Please select a ticket to delete.")

    def back_to_menu(self):
        if self.frame:
            self.frame.destroy()
        self.startup_frame.pack(padx=20, pady=20)

    def toggle_sort_order(self):
        self.sort_recent_first = not self.sort_recent_first
        self.refresh_table()

#---------------------------------------------------------#
    # Show the scanned tickets UI --------------------------------#
    def show_scanned_tickets_ui(self):
        
        self.startup_frame.pack_forget()

        if self.frame:
            self.frame.destroy()
            self.frame = None
            self.tree = None

        self.frame = tk.Frame(self.root, bg="#1d446b")
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        header_frame = tk.Frame(self.frame, bg="#1d446b")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Previously Scanned Tickets:", bg="#1d446b", fg="white", font=("Arial", 14)).pack(side="left", padx=10, pady=10)

        # --- Sort Button ---
        sort_btn_text = tk.StringVar(value="Recent at Bottom")
        def update_sort_btn_text():
            sort_btn_text.set("Recent at Top" if not self.sort_recent_first else "Recent at Bottom")
        def on_sort_btn_click():
            self.toggle_sort_order()
            update_sort_btn_text()
        sort_btn = ttk.Button(header_frame, textvariable=sort_btn_text, command=on_sort_btn_click)
        sort_btn.pack(side="right", padx=30)  # Pack to the right, before the back button

        tk.Button(header_frame, text="Back to Main Menu", command=self.back_to_menu).pack(side="right", padx=10)

        # --- Search Bar ---
        search_frame = tk.Frame(self.frame, bg="#1d446b")
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="Search:", bg="#1d446b", fg="white").pack(side="left", padx=(10, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side="left", padx=(0, 5))

        def perform_search(*args):
            query = search_var.get().lower()
            if not query:
                self.scanned_tickets = self.data_manager.get_ticket_history()
            else:
                all_tickets = self.data_manager.get_ticket_history()
                self.scanned_tickets = [
                    t for t in all_tickets
                    if any(query in str(t.get(field, "")).lower() for field in [
                        "batch_id", "sequence_number", "order_number", "item_number", "door_species", "quantity", "customer", "scan_time"
                    ])
                ]
            self.refresh_table()
            # Scroll to bottom if results exist
            if self.tree.get_children():
                self.tree.see(self.tree.get_children()[-1])

        search_entry.bind("<Return>", perform_search)
        search_btn = ttk.Button(search_frame, text="Search", command=perform_search)
        search_btn.pack(side="left")
        clear_btn = ttk.Button(search_frame, text="Clear", command=lambda: [search_var.set(""), perform_search()])
        clear_btn.pack(side="left", padx=(5, 0))

        # --- Treeview with Scrollbar ---
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("batch_id", "sequence_number", "order_number", "item_number", "door_species", "quantity", "customer", "scan_time"),
            show="headings"
        )

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.heading("batch_id", text="Batch ID")
        self.tree.heading("sequence_number", text="Seq#")
        self.tree.heading("order_number", text="Order#")
        self.tree.heading("item_number", text="Item#")
        self.tree.heading("door_species", text="Door Species")
        self.tree.heading("quantity", text="Qty#")
        self.tree.heading("customer", text="Customer")
        self.tree.heading("scan_time", text="Scan Time")
        
        self.tree.column("batch_id", width=100)
        self.tree.column("sequence_number", width=35)
        self.tree.column("order_number", width=60)
        self.tree.column("item_number", width=60)
        self.tree.column("door_species", width=190)
        self.tree.column("quantity", width=20)
        self.tree.column("customer", width=150)
        self.tree.column("scan_time", width=150)
        self.tree.tag_configure("evenrow", background="#e0e0e0")
        self.tree.tag_configure("oddrow", background="#f5f5f5")

        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)
        delete_btn = ttk.Button(btn_frame, text="Delete Selected Ticket", command=self.delete_selected_ticket)
        delete_btn.pack(side="left", padx=10)

        

        self.tree.bind("<Double-1>", self.on_double_click)

        # ✅ Force reloading from file before refresh
        self.scanned_tickets = self.data_manager.get_ticket_history()
        self.refresh_table()
        # Scroll to bottom after refresh
        if self.tree.get_children():
            self.tree.see(self.tree.get_children()[-1])

