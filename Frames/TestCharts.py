import tkinter as tk
from tkinter.ttk import *

class TestCharts(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Styling
        self["style"] = "Background.TFrame"        

        
    
    