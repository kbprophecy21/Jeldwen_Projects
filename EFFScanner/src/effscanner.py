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

        # Store all matches used for categorization
        self.matches = []

        # Store extended ticket data for later
        self.extended_data = []

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

                            # Minimal data for categorization
                            match_data = {
                                "quantity": int(fields[5]),
                                "door_size": fields[7],
                                "frame_code": fields[8].strip().split()[0]
                            }
                            self.matches.append(match_data)

                            # Extended data for other use
                            extended_data = {
                                "batch_id": self.batch_id,
                                "record_id": fields[0],
                                "press_a": fields[1],
                                "press_b": fields[2],
                                "product_type": fields[3],
                                "operator": fields[4],
                                "quantity": fields[5],
                                "material": fields[6],
                                "door_size": fields[7],
                                "frame_code": fields[8].strip().split()[0],
                                "scan_time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "original_line": line.strip()
                            }

                            self.extended_data.append(extended_data)

                if not self.matches:
                    print(f"❌ No match for '{self.batch_id}' in file.")
                return

        print(f"❌ File '{self.file_name}' not found in {self.folder_path}")

    def get_ticket_data(self):
        """Return minimal match data for categorization."""
        return pd.DataFrame(self.matches) if self.matches else pd.DataFrame()

    def get_extended_data(self):
        """Return extended match data for optional use."""
        return pd.DataFrame(self.extended_data) if self.extended_data else pd.DataFrame()
