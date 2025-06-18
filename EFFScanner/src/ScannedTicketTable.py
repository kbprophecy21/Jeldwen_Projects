import tkinter as tk
from tkinter import ttk, messagebox
from dataManager import DataManager

class ScannedTicketTable:
    def __init__(self, root, startup_frame, scanned_tickets=None, on_update_callback=None, on_delete_callback=None):
        self.root = root
        self.startup_frame = startup_frame
        self.data_manager = DataManager()
        self.scanned_tickets = scanned_tickets if scanned_tickets is not None else []
        self.on_update_callback = on_update_callback
        self.on_delete_callback = on_delete_callback
        self.frame = None  

    def refresh_table(self):
        if not self.tree:
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, ticket in enumerate(self.scanned_tickets):
            self.tree.insert("", "end", iid=str(idx), values=(
                ticket.get("batch_id", ""),
                ticket.get("frame_code", ""),
                ticket.get("door_size", ""),
                ticket.get("quantity", "")
            ))

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        if not row_id or column != "#4":  # Only allow editing quantity (column #4)
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
                self.scanned_tickets[int(row_id)]["quantity"] = new_quantity
                if self.on_update_callback:
                    self.on_update_callback(self.scanned_tickets[int(row_id)])
                self.refresh_table()
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
            ticket = self.scanned_tickets.pop(idx)
            if self.on_delete_callback:
                self.on_delete_callback(ticket)
            self.refresh_table()
        else:
            messagebox.showinfo("No selection", "Please select a ticket to delete.")

    def back_to_menu(self):
        if self.frame:
            self.frame.destroy()
        self.startup_frame.pack(padx=20, pady=20)

    def show_scanned_tickets_ui(self):
        self.startup_frame.pack_forget()
        if self.frame:
            self.frame.destroy()

        self.frame = tk.Frame(self.root, bg="#1d446b")
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Header with Back button
        header_frame = tk.Frame(self.frame, bg="#1d446b")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Previously Scanned Tickets:", bg="#1d446b", fg="white", font=("Arial", 14)).pack(side="left", padx=10, pady=10)
        tk.Button(header_frame, text="Back to Main Menu", command=self.back_to_menu).pack(side="right", padx=10)

        # Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=("batch_id", "frame_code", "door_size", "quantity"),
            show="headings"
        )
        self.tree.heading("batch_id", text="Batch ID")
        self.tree.heading("frame_code", text="Frame Code")
        self.tree.heading("door_size", text="Door Size")
        self.tree.heading("quantity", text="Quantity")
        self.tree.column("batch_id", width=120)
        self.tree.column("frame_code", width=100)
        self.tree.column("door_size", width=100)
        self.tree.column("quantity", width=80)
        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)
        delete_btn = ttk.Button(btn_frame, text="Delete Selected Ticket", command=self.delete_selected_ticket)
        delete_btn.pack(side="left", padx=10)

        # Bind double-click for editing quantity only
        self.tree.bind("<Double-1>", self.on_double_click)

        self.refresh_table()
