import tkinter as tk
from tkinter.ttk import *

class Distortion(Frame):
    def __init__(self, window):
        super().__init__(window)

        
        self["style"] = "Background.TFrame"
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)