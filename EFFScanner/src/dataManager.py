import json
import os
from config_manager import ConfigManager

class DataManager:
    def __init__(self):
        self.config = ConfigManager()
        self.DATA_FILE = self.config.json_save_path
        self.HISTORY_FILE = self.DATA_FILE.replace(".json", "history_scanned_tickets.json")

        # Initialize category totals
        keys = [
            "BF", "MC", "HC", "SC", "MS", "MC 8/0",
            "BF01", "MC01", "HC01", "SC01", "MS01", "MC01 8/0",
            "BF05", "MC05", "HC05", "SC05", "MS05", "MC05 8/0",
            "BF10", "MC10", "HC10", "SC10", "MS10", "MC10 8/0",
            "BF15", "MC15", "HC15", "SC15", "MS15", "MC15 8/0",
            "BF20", "MC20", "HC20", "SC20", "MS20", "MC20 8/0"
        ]
        self.data = {key: 0 for key in keys}
        self.ticket_history = []

        self.load_data()

    def add_ticket(self, ticket_dict):
        required_keys = ["quantity", "frame_code", "door_size"]
        for k in required_keys:
            if k not in ticket_dict:
                print(f"Missing key in ticket: {k} -> {ticket_dict}")
                return  # or raise an error

        quantity = int(ticket_dict.get("quantity", 1))
        frame_code = ticket_dict.get("frame_code") or ticket_dict.get("frame_code")
        door_size = ticket_dict.get("door_size")

        if frame_code and door_size:
            key = self.categorize_ticket(frame_code, door_size, quantity)
            if key:
                self.set_value(key, quantity)
        
        self.ticket_history.append(ticket_dict)
        self.save_data()

    def update_ticket(self, index, new_ticket):
        old_ticket = self.ticket_history[index]
        old_quantity = int(old_ticket.get("quantity", 1))
        old_frame_code = old_ticket.get("frame_code") or old_ticket.get("frame_code")
        old_door_size = old_ticket.get("door_size")

        if old_frame_code and old_door_size:
            old_key = self.categorize_ticket(old_frame_code, old_door_size, old_quantity)
            if old_key:
                self.set_value(old_key, -old_quantity)

        self.ticket_history[index] = new_ticket

        new_quantity = int(new_ticket.get("quantity", 1))
        new_frame_code = new_ticket.get("frame_code") or new_ticket.get("frame_code")
        new_door_size = new_ticket.get("door_size")

        if new_frame_code and new_door_size:
            new_key = self.categorize_ticket(new_frame_code, new_door_size, new_quantity)
            if new_key:
                self.set_value(new_key, new_quantity)

        self.save_data()

    def delete_ticket(self, index):
        ticket = self.ticket_history.pop(index)
        quantity = int(ticket.get("quantity", 1))
        frame_code = ticket.get("frame_code") or ticket.get("frame_code")
        door_size = ticket.get("door_size")

        if frame_code and door_size:
            key = self.categorize_ticket(frame_code, door_size, quantity)
            if key:
                self.set_value(key, -quantity)

        self.save_data()

    def set_value(self, key, value):
        if key in self.data and isinstance(value, (int, float)):
            self.data[key] += value
        else:
            raise KeyError(f"Invalid key or value type: {key}, {value}")

    def get_value(self, key):
        return self.data.get(key, None)

    def get_all(self):
        return self.data.copy()

    def get_total(self):
        return sum(self.data.values())

    def reset_data(self):
        for key in self.data:
            self.data[key] = 0
        self.ticket_history.clear()
        self.save_data()

    def save_data(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.data, f)
        with open(self.HISTORY_FILE, "w") as f:
            json.dump(self.ticket_history, f, indent=4)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as f:
                self.data = json.load(f)
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r") as f:
                self.ticket_history = json.load(f)

    def get_ticket_history(self):
        return self.ticket_history.copy()

    # ----------------------------
    # Category Rules
    # ----------------------------
    def isDoorBifold(self, frame_code):
        frame_letter = frame_code[2].upper()
        return frame_letter in ["F", "J", "W"]

    def isDoorGreaterthan7ft(self, door_size):
        try:
            parts = door_size.upper().split('X')
            if len(parts) == 2:
                height_str = parts[1].strip()
                height = float(height_str)
                return height > 90.0
        except Exception:
            pass
        return False

    def isDoorMCMolded(self, frame_code):
        return frame_code[0].upper() in ["M", "K"]

    def isDoorHCHollowCore(self, frame_code):
        return frame_code[0].upper() == "H"

    def isDoorSCFLushSolid(self, frame_code):
        return frame_code[0].upper() in ["J", "P", "F"]

    def isDoorMSSolidCore(self, frame_code):
        return frame_code[0].upper() == "G"

    def categorize_ticket(self, frame_code, door_size, quantity):
        if self.isDoorBifold(frame_code):
            return self._get_quantity_key("BF", quantity)
        if self.isDoorMCMolded(frame_code):
            if self.isDoorGreaterthan7ft(door_size):
                return self._get_quantity_key("MC", quantity, is_8ft=True)
            return self._get_quantity_key("MC", quantity)
        if self.isDoorHCHollowCore(frame_code):
            return self._get_quantity_key("HC", quantity)
        if self.isDoorSCFLushSolid(frame_code):
            return self._get_quantity_key("SC", quantity)
        if self.isDoorMSSolidCore(frame_code):
            return self._get_quantity_key("MS", quantity)
        return None

    def _get_quantity_key(self, prefix, quantity, is_8ft=False):
        if quantity == 1:
            key = f"{prefix}01"
        elif 2 <= quantity <= 5:
            key = f"{prefix}05"
        elif 6 <= quantity <= 10:
            key = f"{prefix}10"
        elif 11 <= quantity <= 15:
            key = f"{prefix}15"
        elif 16 <= quantity <= 20:
            key = f"{prefix}20"
        else:
            key = prefix

        if is_8ft:
            key += " 8/0"

        return key

    def scan_tickets(self, scanner):
        for _, row in scanner.get_tickets().iterrows():
            quantity = int(row["quantity"])
            door_size = row["door_size"]
            frame_code = row["frame_code"]

            if frame_code and door_size:
                key = self.categorize_ticket(frame_code, door_size, quantity)
                if key:
                    self.set_value(key, quantity)

            self.ticket_history.append(row.to_dict())

        self.save_data()
