import imp
from Frames.NetsFrame import *
from ParameterTab import *
import os
from tkinter import filedialog
from NED_Analyzer import *
import re
import time
import json
from tkinter.ttk import *
from ToggleBtn import *
import matplotlib
from matplotlib import pyplot as plt
from functools import partial

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\grille_default.json'
MESH_OUTPUT_PATH = f'{os.getcwd()}\\Output'

class Grille(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        # f = open(PRESET_PATH, 'r')
        # self.presets = json.load(f)
        # f.close()
        
        self.output_path = tk.StringVar()        
        self.output_path.set(OUTPUT_PATH)        
        self.preset_path.set(PRESET_PATH)
        self.mesh_output_path = tk.StringVar()
        self.mesh_output_path.set(MESH_OUTPUT_PATH)
        self.img_path = tk.StringVar()
        self.mesh_output_type = tk.IntVar()
        self.mesh_output_type.set(1)        
        self.raw_img = None
        
        # preset button event handler config
        self.preset_save_btn.configure(command=self.save_preset)
        self.preset_load_btn.configure(command=self.load_preset)

        # Image Loading 
        self.img_load_frame = LabelFrame(self.settings, text='Image Loading', padding=(5, 5, 5, 5))
        self.img_load_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        self.img_load_input_frame = Frame(self.img_load_frame)
        self.img_load_input_frame.pack(side='top', expand=True, fill='both')
        self.img_load_btn_frame = Frame(self.img_load_frame)
        self.img_load_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.img_path_label = Label(self.img_load_input_frame, text='Image Path')
        self.img_path_label.pack(side='left', padx=5, pady=5)
        self.img_path_input = Entry(self.img_load_input_frame, textvariable=self.img_path)        
        self.img_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        img_load_btn = Button(self.img_load_btn_frame, text='Load', style='Buttons.TButton', command=self.img_load)
        img_load_btn.pack(side='right', padx=2, pady=5)
        img_browse_btn = Button(self.img_load_btn_frame, text='Browse...', style='Buttons.TButton', command=self.img_browse)        
        img_browse_btn.pack(side='right', padx=2, pady=5)

    


    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.grid_extract_paras = self.presets['grid_extract_paras']
        self.grid_sort_paras = self.presets['grid_sort_paras']
        self.grid_extract_settings.parameter_chg(self.grid_extract_paras)
        self.grid_sort_settings.parameter_chg(self.grid_sort_paras)
        
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return 

    def save_preset(self):
        if os.path.isfile(self.preset_path.get()):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(self.preset_path.get(), 'w')
        for p in self.grid_extract_settings.output_values():
            self.grid_extract_paras[p[0]]['value'] = p[1]
        for p in self.grid_sort_settings.output_values():
            self.grid_sort_paras[p[0]]['value'] = p[1]
        
        save_preset = {'grid_extract_paras':self.grid_extract_paras, 'grid_sort_paras':self.grid_sort_paras}
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Saved')
        return

    def path_browse(self, path_var):
        cur_path = os.getcwd()
        temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        path_var.set(temp_path)
        return

    def img_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a image file', filetypes=[("PNG","*.png"), ("bmp","*.bmp"), ("JPG","*.jpg")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.img_path.set(temp_path)
        return

    def img_load(self):        
        img_path = self.img_path.get()
        if len(img_path) > 0:
            self.dist_eval.raw_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            self.update_img(Image.fromarray((self.dist_eval.raw_img).astype(np.uint8)))
            self.console(f'Image File: {img_path} Loaded')
        return
    