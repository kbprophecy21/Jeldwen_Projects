import os
import pandas as pd

class EFFScanner:
    def __init__(self, folder_path, batch_id):
        self.folder_path = folder_path
        self.batch_id = batch_id.strip()

        # Extract press info
        self.group_press = self.batch_id[-7:]
        self.group_press_A = self.group_press[:4]
        self.group_press_B = self.group_press[4:]

        # Extract file name
        self.file_name = f"{self.batch_id[:-7]}.LIS"
        self.file_path = None

        # Store all ticket data (full extraction)
        self.tickets = []

    def find_ticket(self):
        for file in os.listdir(self.folder_path):
            if file == self.file_name:
                self.file_path = os.path.join(self.folder_path, file)
                print(f"Processing file: {self.file_path}")

                with open(self.file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        fields = line.strip().split(",")
                        search_range = [field.strip('"') for field in fields[1:5]]

                        if self.group_press_A in search_range and self.group_press_B in search_range:
                            fields = [field.strip('"') for field in fields]
                            ticket_data = {
                                "batch_id": self.batch_id,
                                "press_a": fields[3],
                                "press_b": fields[4],
                                "quantity": fields[5],
                                "door_size": fields[7],
                                "door_species": fields[8],
                                "frame_code": fields[8].strip().split()[0],
                                "customer": fields[17],
                                "order_number": fields[18],
                                "item_number": fields[19],
                                "sequence_number": fields[20],
                                "scan_time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "original_line": line.strip()
                            }
                            self.tickets.append(ticket_data)

                if not self.tickets:
                    print(f"❌ No match for '{self.batch_id}' in file.")
                return

        print(f"❌ File '{self.file_name}' not found in {self.folder_path}")

    def get_tickets(self):
        """Return all extracted ticket data as a DataFrame."""
        return pd.DataFrame(self.tickets) if self.tickets else pd.DataFrame()
