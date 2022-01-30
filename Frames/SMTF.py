import tkinter as tk
from tkinter.ttk import *

class SMTF(Frame):
    def __init__(self, parent, controller, show_timer):
        super().__init__(parent)

        
        self["style"] = "Background.TFrame"
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)