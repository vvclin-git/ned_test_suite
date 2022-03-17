import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image, ImageTk

import os
import json
from tkinter import filedialog

class PresetFileLoad(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        self.controller = None
        self.preset_path = tk.StringVar()
        self.preset = None        
        
        self.preset_frame = LabelFrame(self, text='Parameter Preset', padding=(5, 5, 5, 5))
        self.preset_frame.pack(expand=True, fill='x', pady=5, side='top')

        self.preset_input_frame = Frame(self.preset_frame)
        self.preset_input_frame.pack(side='top', expand=True, fill='both')
        self.preset_btn_frame = Frame(self.preset_frame)
        self.preset_btn_frame.pack(side='top', expand=True, fill='both')

        self.preset_path_label = Label(self.preset_input_frame, text='Preset Path')
        self.preset_path_label.pack(side='left', padx=5, pady=5)
        self.preset_path_input = Entry(self.preset_input_frame, textvariable=self.preset_path)
        self.preset_path_input.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        
        self.preset_save_btn = Button(self.preset_btn_frame, text='Save As...', style='Buttons.TButton', command=self.save_preset)        
        self.preset_save_btn.pack(side='right', padx=2, pady=5)
        self.preset_load_btn = Button(self.preset_btn_frame, text='Load...', style='Buttons.TButton', command=self.load_preset)
        self.preset_load_btn.pack(side='right', padx=2, pady=5)
        self.preset_browse_btn = Button(self.preset_btn_frame, text='Browse...', style='Buttons.TButton', command=self.browse_preset)
        self.preset_browse_btn.pack(side='right', padx=2, pady=5)
    
    def load_preset(self, load_func):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        load_func()
        return
    
    def save_preset(self):
        preset_path = self.preset_path.get()
        if os.path.isfile(preset_path):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(preset_path, 'w')
        save_preset = self.presets
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {preset_path} Saved')
        return

    def browse_preset(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return
       