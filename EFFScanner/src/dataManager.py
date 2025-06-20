import json
import os
from config_manager import ConfigManager

class DataManager:
    def __init__(self):
        self.config = ConfigManager()
        self.DATA_FILE = self.config.json_save_path

        # Initialize structure
        self.data = {
            "category_totals": self._init_category_totals(),
            "scanned_tickets": [],
            "total_count": 0
        }

        self.load_data()

    def _init_category_totals(self):
        keys = [
            "BF", "MC", "HC", "SC", "MS", "MC 8/0",
            "BF01", "MC01", "HC01", "SC01", "MS01", "MC01 8/0",
            "BF05", "MC05", "HC05", "SC05", "MS05", "MC05 8/0",
            "BF10", "MC10", "HC10", "SC10", "MS10", "MC10 8/0",
            "BF15", "MC15", "HC15", "SC15", "MS15", "MC15 8/0",
            "BF20", "MC20", "HC20", "SC20", "MS20", "MC20 8/0"
        ]
        return {key: 0 for key in keys}

    def add_ticket(self, ticket_dict):
        required_keys = ["quantity", "frame_code", "door_size"]
        if not all(k in ticket_dict for k in required_keys):
            print(f"Missing keys in ticket: {ticket_dict}")
            return

        quantity = int(ticket_dict["quantity"])
        frame_code = ticket_dict["frame_code"]
        door_size = ticket_dict["door_size"]

        key = self.categorize_ticket(frame_code, door_size, quantity)
        if key:
            self.set_value(key, quantity)

        self.data["scanned_tickets"].append(ticket_dict)
        self.data["total_count"] += quantity
        self.save_data()

    def delete_ticket_by_data(self, ticket_to_delete):
        quantity = int(ticket_to_delete.get("quantity", 1))
        frame_code = ticket_to_delete.get("frame_code")
        door_size = ticket_to_delete.get("door_size")

        key = self.categorize_ticket(frame_code, door_size, quantity)
        if key:
            self.set_value(key, -quantity)

        self.data["scanned_tickets"] = [
            t for t in self.data["scanned_tickets"]
            if not (
                t.get("batch_id") == ticket_to_delete.get("batch_id") and
                t.get("item_number") == ticket_to_delete.get("item_number") and
                t.get("scan_time") == ticket_to_delete.get("scan_time")
            )
        ]

        self.data["total_count"] -= quantity
        self.save_data()

    def reprocess_ticket(self, old_ticket, new_ticket):
        old_quantity = int(old_ticket.get("quantity", 1))
        old_key = self.categorize_ticket(old_ticket["frame_code"], old_ticket["door_size"], old_quantity)
        if old_key:
            self.set_value(old_key, -old_quantity)

        new_quantity = int(new_ticket.get("quantity", 1))
        new_key = self.categorize_ticket(new_ticket["frame_code"], new_ticket["door_size"], new_quantity)
        if new_key:
            self.set_value(new_key, new_quantity)

        for i, t in enumerate(self.data["scanned_tickets"]):
            if (
                t.get("batch_id") == old_ticket.get("batch_id") and
                t.get("sequence_number") == old_ticket.get("sequence_number")
            ):
                self.data["scanned_tickets"][i] = new_ticket
                break

        self.data["total_count"] += new_quantity - old_quantity
        self.save_data()

    def set_value(self, key, value):
        if key in self.data["category_totals"] and isinstance(value, (int, float)):
            self.data["category_totals"][key] += value
        else:
            raise KeyError(f"Invalid key or value type: {key}, {value}")

    def get_all(self):
        return self.data["category_totals"].copy()

    def get_total(self):
        return self.data["total_count"]

    def get_ticket_history(self):
        return self.data["scanned_tickets"].copy()

    def reset_data(self):
        self.data["category_totals"] = self._init_category_totals()
        self.data["scanned_tickets"] = []
        self.data["total_count"] = 0
        self.save_data()
        self.load_data()

    def save_data(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as f:
                self.data = json.load(f)

    # ---- Categorization Logic ---- #

    def isDoorBifold(self, frame_code):
        return frame_code[2].upper() in ["F", "J", "W"]

    def isDoorGreaterthan7ft(self, door_size):
        try:
            parts = door_size.upper().split('X')
            if len(parts) == 2:
                height = float(parts[1].strip())
                return height > 90.0
        except:
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
