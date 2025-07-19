import os
from effscanner import EFFScanner
from dataManager import DataManager
from windowsGUI import EFFApp
import tkinter as tk
import LISmanager


 

def main():
    
    root = tk.Tk() 
    app = EFFApp(root)
    app.run_app()

if __name__ == "__main__":
    main()
