import os
from datetime import datetime, timedelta
from config_manager import ConfigManager


class LISmanager:
    
    def __init__(self):
        
        self.config = ConfigManager() 
        self.data_folder_path = self.config.data_folder
        
        
        
        
    #------------METHODS--------------------#
    
    def cleanUp(self):
        
        if os.path.exists(self.data_folder_path):
            print("File doesn't not exist")
            return
        
        cutoff_date = datetime.now - timedelta(days=13)
            
        for filename in os.listdir(self.data_folder_path):
            if filename.endswith(".LIS"):
                try:
                    file_date = datetime.strptime(filename[:6], "%m%d%y")
                    if file_date < cutoff_date:
                        file_path = os.path.join(self.data_folder_path, filename)
                        os.remove(file_path)
                        print(f'Removed: {filename}')
                except ValueError:
                    print(f"Skipping Invalid {filename}")